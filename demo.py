import time
from executor import execute_plan

def main():
    print("🎭 Starting Philips Ideathon 3-Stage Demo Workflow 🎭\\n")
    
    tasks = [
        (
            "Open Excel, enter a 5-row sales table, add a chart, save as SalesReport.xlsx", 
            ["open_excel"]
        ),
        (
            "Open Word, write a 3-paragraph project summary report, save as Report.docx", 
            ["open_word"]
        ),
        (
            "Open Outlook, compose an email to test@example.com with subject 'Automated Report' and attach the files created above, send it", 
            ["open_outlook"]
        )
    ]
    
    for i, (desc, plan) in enumerate(tasks):
        print(f"\\n--- 🚀 Demo Phase {i+1} ---")
        print(f"Goal: {desc}")
        print(f"Plan: {plan}\\n")
        
        def cb(step, status, msg, **kwargs):
            if status == "running":
                print(f"  [⏳] {step}: {msg}")
            elif status == "done":
                print(f"  [✅] {step}: {msg}")
            elif status == "error":
                print(f"  [❌] {step}: {msg}")
            elif status == "thoughts":
                print(f"  [🧠] {step}: {msg}")
                
        execute_plan(plan, desc, status_callback=cb)
        
        if i < len(tasks) - 1:
            print("\\n⏳ Pausing for 5 seconds before next demonstration phase...")
            time.sleep(5)
        
    print("\\n🎉 Ideathon Demo Concluded successfully!")

if __name__ == "__main__":
    main()
