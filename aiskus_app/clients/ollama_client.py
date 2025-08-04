import ollama
from ollama import Client
from ..models.question import Question

summaries_prompt_directions = """
        You are an educational analytics assistant analyzing student questions to identify learning patterns and provide insights for instructors.

        **Your Task:**
        Analyze the provided student questions and chat context to identify themes, knowledge gaps, and student sentiment.

        **Analysis Guidelines:**

        1. **Theme Identification:**
        - Identify 3-5 main themes that capture the core areas of student confusion
        - Use concise, descriptive phrases (1-5 words each)
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

1. **summary**: A concise, scannable summary structured as:
   - Key Struggle Areas: 3-4 easy-to-read and understandable sentences communicating the most critical knowledge gaps, connecting ideas and highlighting any persistent patterns in the knowledge gaps across multiple sessions.
   - Next Steps: 2-3  3-4 easy-to-read and understandable sentences describing teaching approach adjustments which can be made in order to successfully provide clarity & address the knowledge gaps. Suggestions
   can include asking the students specfic clarifying questions, or even wlaking through a specifc example.
    Please seperate sentences into new lines when making a different points, make the summary easier to view & read visually by breaking up paragraph structure.

2. **themes**: A consolidated list of the most significant themes. Extract and deduplicate themes from all batches, keeping only the most meaningful ones (maximum 10 themes). Use 1-5 words per theme.

3. **number_of_questions**: Calculate as 10 * (number of metadata items in the input list)

4. **generated_time**: Use the current timestamp when generating this report

5. **student_headspace**: Single sentence describing the class mood to help teacher adapt teaching style

**Critical JSON Formatting Rules:**
- Use \\n for line breaks within the summary string
- Do not include actual line breaks or control characters
- Escape all special characters properly
- Test JSON validity before responding

**Summary Writing Guidelines:**
- Use bullet points for Key Struggling Areas and Immediate Actions
- Keep each bullet point to 1-2 lines maximum
- For struggling areas, explicitly note if issues appear across multiple sessions
- Focus on the most critical 2-3 issues, not every problem mentioned
- Make action recommendations focus on teaching method types rather than specific examples
- Use active voice and concrete language

**Example Output Format:**

{
  "summary": "Key Struggling Areas:\\n analysis goes here \\n Next Steps:\\n imporvements go here",
  "themes": ["linear algebra", "derivative rules", "integration by parts", "matrix multiplication"],
  "number_of_questions": 30,
  "generated_time": 1672531200,
  "student_headspace": "Students are frustrated around complicated concepts but eager to learn."
}

**Important:** 
- Do not hallucinate information not present in the input
- Focus on patterns that appear across multiple batches
- Consolidate similar themes intelligently
- Keep summary under 120 words total
- Ensure JSON is valid and properly formatted with escaped newlines
- Use \\n instead of actual line breaks in the summary field

The required keys in the returned response are: 1.summary, 2.themes, 3.number_of_questions, 4.generated_time, 5.student_headspace

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


    
