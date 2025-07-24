import time

class SummaryRequest:

    __slots__=("summary_requested_time", "summary_end_range")

    def __init__(self, summary_requested_time: int = None):
        self.summary_requested_time = summary_requested_time or int(time.time())
        self.summary_end_range = self.summary_requested_time + 600
         # default initilizing the summary end range to 10 minutes after the summary requested time

    def to_dict(self):
        return{
            'summary_requested_time': self.summary_requested_time,
            'summary_end_range': self.summary_end_range
        }

    def __repr__(self):
        return f"SummaryRequest(summary_requested_time={self.summary_requested_time}, summary_end_range={self.summary_end_range})"