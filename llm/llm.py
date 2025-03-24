from langchain_core.messages import HumanMessage

from llm.graph import build_graph

def call(question: str):
    try:    
        graph = build_graph()
        result = graph.invoke({"messages": [HumanMessage(content=question)]})
        answer = result['messages'][-1].content
        print(f"\nAnswer: \n\n{answer}")
        return answer 
    except Exception as e:
        print(e)
        return "No result"