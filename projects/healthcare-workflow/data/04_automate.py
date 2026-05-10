"""
04_automate.py
==============
NHS Healthcare Workflow Analytics Pipeline
STEP 4 — FULL PIPELINE AUTOMATION

Runs the entire pipeline in sequence:
  Step 1 → 01_extract.py    (download NHS data)
  Step 2 → 02_clean.py      (clean and standardise)
  Step 3 → 03_calculate_kpis.py (calculate all KPIs)
  Step 4 → 05_email_report.py   (build and send email)

One command runs everything:
  python 04_automate.py

Scheduling:
  Windows  — Task Scheduler → run every Monday 07:00
  Mac/Linux— Cron: 0 7 * * 1 python /path/to/04_automate.py

Author: Taiwo Tobi Omoyeni
"""

import os, sys, time, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log(msg, level="INFO"):
    symbols = {"INFO": "  ", "OK": "✅", "FAIL": "❌", "STEP": "▶", "DIVIDER": "─"}
    sym = symbols.get(level, "  ")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {sym} {msg}")

def run_step(step_num, module_name, description):
    """Import and run a pipeline step, capturing success/failure."""
    log(f"STEP {step_num} — {description}", "STEP")
    start = time.time()
    try:
        import importlib
        mod = importlib.import_module(module_name)
        # Call the main function of each module
        main_funcs = {
            "01_extract":         "main",
            "02_clean":           "clean_data",
            "03_calculate_kpis":  "calculate_kpis",
            "05_email_report":    "main",
        }
        func_name = main_funcs.get(module_name)
        if func_name and hasattr(mod, func_name):
            getattr(mod, func_name)()
        elapsed = round(time.time() - start, 1)
        log(f"Step {step_num} completed in {elapsed}s", "OK")
        return True, elapsed
    except SystemExit:
        elapsed = round(time.time() - start, 1)
        log(f"Step {step_num} completed in {elapsed}s", "OK")
        return True, elapsed
    except Exception as e:
        elapsed = round(time.time() - start, 1)
        log(f"Step {step_num} FAILED: {e}", "FAIL")
        return False, elapsed

def main():
    start_time = time.time()
    print()
    print("=" * 60)
    print("  NHS HEALTHCARE WORKFLOW ANALYTICS PIPELINE")
    print("  Automated Run —", datetime.now().strftime("%A %d %B %Y %H:%M"))
    print("  Author: Taiwo Tobi Omoyeni")
    print("=" * 60)
    print()

    pipeline = [
        ("01_extract",        "Data Extraction (NHS RTT)"),
        ("02_clean",          "Data Cleaning & Standardisation"),
        ("03_calculate_kpis", "KPI Calculation"),
        ("05_email_report",   "Email Report Generation & Delivery"),
    ]

    results = []
    for module, description in pipeline:
        success, elapsed = run_step(len(results) + 1, module, description)
        results.append({
            "step":        module,
            "description": description,
            "success":     success,
            "elapsed_s":   elapsed,
        })
        if not success:
            log(f"Pipeline halted at step {len(results)}. Fix the error and re-run.", "FAIL")
            break
        print()

    # ── Pipeline summary ──────────────────────────────────────
    total_time = round(time.time() - start_time, 1)
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed

    print("=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        print(f"  Step {i}: {status} — {r['description']} ({r['elapsed_s']}s)")
    print()
    print(f"  Steps passed : {passed} / {len(pipeline)}")
    print(f"  Total time   : {total_time}s")
    print(f"  Completed at : {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    # ── Save run log ──────────────────────────────────────────
    from config import OUTPUTS_DIR
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    log_path = os.path.join(OUTPUTS_DIR, "pipeline_log.json")
    with open(log_path, "w") as f:
        json.dump({
            "run_timestamp": datetime.now().isoformat(),
            "total_seconds": total_time,
            "steps_passed":  passed,
            "steps_failed":  failed,
            "results":       results,
        }, f, indent=2)
    print(f"\n  Run log saved: outputs/pipeline_log.json")

    if failed == 0:
        print("\n  🎉 Pipeline completed successfully!")
        print("     Dashboard JSON files are updated.")
        print("     Email report sent to configured recipients.")
    else:
        print(f"\n  ⚠️  Pipeline completed with {failed} failure(s).")
        print("     Check the error messages above and re-run.")
    print()

if __name__ == "__main__":
    main()
