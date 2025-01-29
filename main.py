import subprocess
from random import sample

from slack_bolt import App
from slack_sdk import WebClient
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_SIGNATURE = os.environ['SLACK_SIGNATURE']
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNATURE)

def upload_frog_image():
    local_image_path = os.path.join("./images", sample(os.listdir("./images"), 1)[0])
    channel_id = "C04JF91SKUJ"

    quote = subprocess.Popen(['fortune'], stdout=subprocess.PIPE).communicate()[0].decode()
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        response = client.files_upload_v2(
            channels=channel_id,
            file=local_image_path,
            title="Daily Frog 🐸",
            initial_comment=quote
        )
        if not response["ok"]:
            print(f"Error uploading file: {response['error']}")
        else:
            print(f"Frog image uploaded at {datetime.now()}")
    except Exception as e:
        print(f"Error uploading file: {e}")

@app.command("/frog")
def handle_frog_command(ack, body, client: WebClient):
    ack()

    local_image_path = os.path.join("./images", sample(os.listdir("./images"), 1)[0])
    try:
        response = client.files_upload_v2(
            channels=body["channel_id"],
            file=local_image_path,
            title="Here's a frog for you!",
            initial_comment="🐸 A cute frog just for you!"
        )
        if not response["ok"]:
            print(f"Error uploading file: {response['error']}")
    except Exception as e:
        print(f"Error uploading file: {e}")

@app.event("message")
def react_to_frog_messages(event, client: WebClient):
    text = event.get("text", "").lower()
    if "frog" in text:
        try:
            response = client.reactions_add(
                channel=event["channel"],
                timestamp=event["ts"],
                name="frog"
            )
            if not response["ok"]:
                print(f"Error adding reaction: {response['error']}")
        except Exception as e:
            print(f"Error adding reaction: {e}")


@app.event("app_mention")
def respond_to_mention(event, say):
    ribbit_count = random.randint(1, 10)
    ribbits = " ".join(["ribbit"] * ribbit_count)
    say(f"{ribbits}! 🐸")


# Schedule the daily task
scheduler = BackgroundScheduler()
scheduler.add_job(upload_frog_image, "cron", hour=9, minute=0)
scheduler.start()

# Start the Slack app
if __name__ == "__main__":
    upload_frog_image()
    app.start(port=3000)
