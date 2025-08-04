import ollama
from ollama import Client
from ..models.question import Question

summaries_prompt_directions = """
        You are an educational analytics assistant analyzing student questions to identify learning patterns and provide insights for instructors.

        **Your Task:**
        Analyze the provided student questions and chat context to identify themes, knowledge gaps, and student sentiment.

        **Analysis Guidelines:**

        1. **Theme Identification:**
        - Identify 3-7 main themes that capture the core areas of student confusion
        - Use concise, descriptive phrases (2-5 words each)
        - Look for overlapping patterns and consolidate related concepts
        - Focus on conceptual areas rather than specific question details
        - Use educational terminology that instructors would recognize

        2. **Summary Structure:**
        Create a summary as a single string with exactly three tagged paragraphs:

        **(1) Knowledge Gaps Analysis:**
        - Summarize the primary knowledge gaps revealed by current questions
        - Reference recurring confusion patterns from chat history when relevant
        - Focus on conceptual understanding issues, not just procedural mistakes
        - Be specific about which foundational concepts are missing

        **(2) Instructor Recommendations:**
        - Provide 2-3 concrete, actionable teaching strategies
        - Suggest specific concepts to revisit or reinforce
        - Recommend pedagogical approaches (visual aids, examples, practice types)
        - Consider the emotional state of students in your recommendations
        - Connect advice to the specific gaps identified in paragraph (1)

        **(3) Student Sentiment Summary:**
        - Provide ONE concise sentence capturing overall student emotional state
        - Include engagement level, frustration indicators, and confidence patterns
        - Use descriptive language that helps instructors gauge class mood

        **Context Usage:**
        - Use the provided message history to identify recurring themes across sessions
        - Connect current questions to previous patterns when relevant
        - Do NOT create themes or patterns not supported by the actual questions
        - Weight recent patterns more heavily than older ones

        **Output Format:**
        Return ONLY a valid JSON object with these exact keys:
        {
        "first_question_time": <integer_timestamp>,
        "last_question_time": <integer_timestamp>,
        "themes": ["theme1", "theme2", "theme3"],
        "summary": "(1) Knowledge gaps paragraph...\n(2) Teaching recommendations paragraph...\n(3) Student sentiment sentence."
        }
        text

        **Quality Requirements:**
        - Each paragraph must start with its exact tag: "(1)", "(2)", or "(3)"
        - Separate paragraphs with single newline characters (\n)
        - Keep themes list between 3-7 items
        - Ensure themes are distinct and meaningful
        - Make recommendations specific and actionable
        - Base sentiment analysis on actual question tone and content

        **Example Output:**
        {
        "first_question_time": 1672531200,
        "last_question_time": 1672534800,
        "themes": ["derivative applications", "chain rule confusion", "notation interpretation"],
        "summary": "(1) Students demonstrate fundamental gaps in understanding derivative applications, particularly struggling with the chain rule when applied to composite functions and interpreting mathematical notation in complex expressions.\n(2) Instructors should provide more step-by-step worked examples of chain rule applications, use visual representations of composite functions, and dedicate time to explaining mathematical notation conventions before introducing new derivative techniques.\n(3) Students show high engagement but increasing frustration with notation complexity."
        }
        text

        Here are the student questions & context:

        """
report_prompt_directions ="""
        You are an educational analytics assistant. You will receive a list of summary metadata objects, each containing themes and summaries from batches of student questions. Your task is to create a comprehensive report that combines all this information into a meaningful overview.

        **Input Format:**
        You will receive a list of dictionaries, each containing:
        - id: unique identifier
        - themes: JSON string containing list of themes from that batch
        - summary_str: three-paragraph summary string with tags (1), (2), (3)

        **Your Task:**
        Analyze all the provided summary metadata and create a unified report that synthesizes the information across all batches.

        **Output Requirements:**
        Return your response as a valid JSON object with exactly the below keys:

        1. **summary**: A comprehensive summary combining insights from all summary_str fields. Structure this as:
        - First paragraph: Overall knowledge gaps and difficulties across all batches
        - Second paragraph: Consolidated advice for the teacher based on all patterns observed
        - Third paragraph: Overall student sentiment analysis across all sessions
        Ensure "summary" is spelled correctly.

        2. **themes**: A consolidated list of the most significant themes. Extract and deduplicate themes from all batches, keeping only the most meaningful ones (maximum 10 themes). Use 1-5 words per theme.

        3. **number_of_questions**: Calculate as 10 * (number of metadata items in the input list)

        4. **generated_time**: Use the current timestamp when generating this report
       
        5. **student_headspace**: single sentence to represent the mood of the class to help teacher adapt teaching style

        **Guidelines:**
        - Identify recurring patterns across multiple summary batches
        - Consolidate similar themes (e.g., "calculus derivatives" and "derivative confusion" should be merged)
        - In the summary, highlight which concepts appear consistently problematic across sessions
        - Provide actionable insights for the teacher based on the aggregate data
        - Maintain the emotional tone analysis from individual summaries to create an overall class sentiment

        **Example Output Format:**     
            
        {
        "summary": "Paragraph 1 about overall gaps... Paragraph 2 about teacher advice... Paragraph 3 about student sentiment...",
        "themes": ["linear algebra", "derivative rules", "integration by parts", "matrix multiplication"],
        "number_of_questions": 30,
        "generated_time": 1672531200,
        "student_headspace": "The students are frustrated due around complicated concepts but eager to learn."
        }

        **Important:** 
        - Do not hallucinate information not present in the input
        - Focus on patterns that appear across multiple batches
        - If themes are similar, consolidate them intelligently
        - Ensure the JSON is valid and properly formatted

        The required keys in the returned response are 1.summary, 2.themes, 3. number_of_questions, 4.generated_time, 5. student_headspace

        Here is the summary metadata to analyze:

                """

class OllamaClient:

    def __init__(self, localhost='http://localhost:11434'):
        self.ollama_client_object = Client(host=localhost)
        self.message_history = []

    """
    summary_request
    Parameters: list of batched question obhects from the question processor

    Receives the list of questions. Sends them in a chat to the model, along with the prompt:
        - prompt goals:
            - extract themes
    
    """

    def summary_request (self,batched_messages: list[Question]):
        question_input = summaries_prompt_directions + str(batched_messages)
        response = self.ollama_client_object.chat(
            model='gemma3n:e4b', 
            messages=[{'role': 'user','content': self.message_history},
                      {'role': 'user', 'content': question_input},
                    ]
            )
        
        # adding the model response to the memory
        self.message_history += [
            {'role':'user','content':question_input},
            {'role': 'assistant', 'content': response.message.content},
        ]

        return response
    
    """
    Report Request:
        Receives list of dict metadata, each item in the dictioary representing a processed summary batch from the DB.
        Take the dictonary, and prompt model to generate a meaninful report JSON easily accessed by fronted.
        {
            themes: (list str)
            summary: (str block)
            numQs: (int for batch size?)
            generated time (epoch)

        }

        returned
    """

    def create_report(self,requested_report_metadata_list: list[dict]):
        report_prompt = report_prompt_directions + str(requested_report_metadata_list) 
        report = self.ollama_client_object.chat(model="gemma3n:e4b", messages=[
            {
            'role': 'user',
            'content': report_prompt,
            },
        ])

        return report


    
