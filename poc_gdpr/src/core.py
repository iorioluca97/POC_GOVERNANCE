from agents import Agent, Runner

user_identification_agent = Agent(
    name="User Identification Agent",
    instructions="""
    Verify the following user information are present in the text below. 
    The response should be a JSON object with the following:
    - name
    - city
    - phone_number
    - email
    - fiscal_code

    DO NOT include any character other than the dictionary in the response.
    
    The user information is:
    
    """

    ,
    handoffs=[]
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are a Data Quality Triage Agent. Your job is to determine which agent to use based on the user's input.
    """,
    handoffs=[
        user_identification_agent
    ]
)
