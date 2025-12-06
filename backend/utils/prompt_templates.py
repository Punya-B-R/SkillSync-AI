"""
Prompt templates for AI interactions.
"""

class PromptTemplates:
    """Templates for generating AI prompts."""
    
    @staticmethod
    def resume_analysis_prompt(resume_text):
        """
        Generate prompt for resume analysis.
        
        Args:
            resume_text: Text content of resume
            
        Returns:
            str: Formatted prompt
        """
        # TODO: Create prompt template for resume analysis
        # TODO: Include instructions for extracting skills, experience, education
        # TODO: Return formatted prompt
        pass
    
    @staticmethod
    def domain_recommendation_prompt(resume_data, interests):
        """
        Generate prompt for domain recommendations.
        
        Args:
            resume_data: Parsed resume data
            interests: List of user interests
            
        Returns:
            str: Formatted prompt
        """
        # TODO: Create prompt template for domain recommendations
        # TODO: Include resume data and interests
        # TODO: Request structured output with domain names and descriptions
        # TODO: Return formatted prompt
        pass
    
    @staticmethod
    def roadmap_generation_prompt(domain, time_commitment, resume_data):
        """
        Generate prompt for roadmap generation.
        
        Args:
            domain: Selected career domain
            time_commitment: Time commitment string
            resume_data: Parsed resume data
            
        Returns:
            str: Formatted prompt
        """
        # TODO: Create prompt template for roadmap generation
        # TODO: Include domain, time commitment, and resume data
        # TODO: Request structured roadmap with phases, milestones, and tasks
        # TODO: Specify output format (JSON or structured text)
        # TODO: Return formatted prompt
        pass
    
    @staticmethod
    def chat_prompt(message, context=None):
        """
        Generate prompt for AI chat.
        
        Args:
            message: User message
            context: Optional context (roadmap, resume)
            
        Returns:
            str: Formatted prompt
        """
        # TODO: Create prompt template for chat
        # TODO: Include context if provided
        # TODO: Return formatted prompt
        pass

