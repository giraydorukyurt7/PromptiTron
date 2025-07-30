# agents/crewai_agents.py

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def run(self, input_data):
        raise NotImplementedError


class SummaryAgent(BaseAgent):
    def run(self, input_data):
        from modules.summarizer import summarize_text
        return summarize_text(input_data["text"])


class QuizAgent(BaseAgent):
    def run(self, input_data):
        from modules.quizgenerator import generate_quiz
        return generate_quiz(input_data["text"])


class WorldcloudAgent(BaseAgent):
    def run(self, input_data):
        from modules.worldcloud_module import generate_wordcloud
        return generate_wordcloud(input_data["text"])


class MindmapAgent(BaseAgent):
    def run(self, input_data):
        from modules.mindmap import generate_mindmap
        return generate_mindmap(input_data["text"])


class StudyPlanAgent(BaseAgent):
    def run(self, input_data):
        from modules.studyplanner import create_study_plan
        return create_study_plan(input_data["text"])