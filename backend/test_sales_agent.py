# test_sales_agent_conversation.py
from agents.sales_agent import SalesAgent

if __name__ == "__main__":
    agent = SalesAgent()
    # Run interactive chat; data will be returned for chaining to other agents,
    # but we do not print the raw dict to the end user.
    final_data = agent.interactive_chat()
    # Developer note: use final_data in the Master Agent / next worker,
    # do not expose this structured dict directly to the customer.