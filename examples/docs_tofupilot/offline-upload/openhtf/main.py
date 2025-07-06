from tofupilot import TofuPilotClient

client = TofuPilotClient()


def main():
    # Replace with actual path of your report
    file_path = "data/PCB01A69658.openhtf_test.2025-01-20_15-32-06-058.json"
    client.create_run_from_openhtf_report(file_path)


if __name__ == "__main__":
    main()
