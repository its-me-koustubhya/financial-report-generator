# if __name__ == "__main__":
#    test_state = {
#       "user_input": "tesla",
#       "raw_data":[],
#       "data_sources":[],
#       "messages":[]
#    }

#    result = data_collector_agent(test_state)
#    print(f"found {len(result['raw_data'])} chunks of data")
#    print(f"Sources: {len(result['data_sources'])}")

# if __name__ == "__main__":
#     test_state = {
#         "user_input": "Tesla",
#         "raw_data": [
#             "Tesla reported revenue of $96.8 billion in 2023, up 19% from previous year.",
#             "Tesla's net income was $15 billion in 2023. The company delivered 1.8 million vehicles.",
#             "Stock price has grown 120% year over year. Market cap exceeds $800 billion."
#         ],
#         "insights": [],
#         "trends": [],
#         "messages": []
#     }
    
#     result = analyst_agent(test_state)
#     print("Key Metrics:", result['key_metrics'])
#     print("\nInsights:", result['insights'])
#     print("\nTrends:", result['trends'])
#     print("\nMessages:", result['messages'])

# if __name__ == "__main__":
#     test_state = {
#         "user_input": "Tesla",
#         "key_metrics": {
#             "revenue": "$96.8 billion (2023)",
#             "profit": "$15 billion net income",
#             "growth_rate": "19% YoY revenue growth"
#         },
#         "insights": [
#             "Strong revenue growth driven by vehicle deliveries",
#             "Improving profit margins due to operational efficiency"
#         ],
#         "trends": [
#             "Expanding production capacity globally",
#             "Stock price appreciation of 120% YoY"
#         ]
#     }
    
#     result = writer_agent(test_state)
#     print("Report Generated:")
#     print("="*50)
#     print(result['final_report'])
#     print("="*50)
#     print(f"Status: {result['messages']}")

# if __name__ == "__main__":
#     app = create_report_workflow()
    
#     initial_state = {
#         "user_input": "FakeCompanyDoesNotExist999",
#         "analysis_focus": None,
#         "raw_data": [],
#         "data_sources": [],
#         "key_metrics": None,
#         "insights": [],
#         "trends": [],
#         "report_sections": None,
#         "final_report": "",
#         "current_step": "",
#         "messages": [],
#         "data_collection_attempts": 0,
#         "writing_attempts": 0 
#     }
    
#     print("🚀 Starting intelligent report generation workflow...")
#     print("="*60)
    
#     result = app.invoke(initial_state)
    
#     print("\n" + "="*60)
#     print("✅ Workflow completed!")
#     print("="*60)
    
#     print(f"\n📊 Final Statistics:")
#     print(f"  - Data collection attempts: {result.get('data_collection_attempts', 0)}")
#     print(f"  - Writing attempts: {result.get('writing_attempts', 0)}")
#     print(f"  - Total sources: {len(result.get('data_sources', []))}")
#     print(f"  - Report length: {len(result.get('final_report', ''))} chars")
    
#     print(f"\n📝 Messages:")
#     for msg in result['messages']:
#         print(f"  - {msg}")
    
#     print(f"\n📄 Final Report Preview:")
#     print("="*60)
#     print(result['final_report'][:500] + "...")

# Create a test file: test_config.py
from config import settings

print("✅ Configuration loaded successfully!")
print(f"Model: {settings.MODEL_NAME}")
print(f"Database URL set: {bool(settings.DATABASE_URL)}")
print(f"Secret key length: {len(settings.SECRET_KEY)}")