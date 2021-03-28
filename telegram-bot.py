import time
from datetime import datetime as DateTime
from typing import Optional

from telegram import Message
from telegram.ext import Updater, MessageHandler, Filters


#----------------------------------------------------------------------------------------------------------------------
# Alarm
THRESHOLD_TEMP = [15.0, 25.0, "Temperature", "°C"]
THRESHOLD_RH   = [0.0, 100.0, "Humidity", "%RH"]


# Telegram
TELEGRAM_BOT_API_KEY = 'YOUR API KEY HERE'


# Sensor
try:
    import Adafruit_DHT
except ImportError:
    print("WARN> using dummy driver. If you want to use an actual Adafruit DHT device, please install the pip.")
    import ada_dht as Adafruit_DHT
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4


#----------------------------------------------------------------------------------------------------------------------
# Globals
LOW, NORMAL, HIGH = (-1, 0, 1)
message_queue = []
last_message: Optional[Message] = None


#----------------------------------------------------------------------------------------------------------------------
def send_message(text):
    #global message_queue

    if last_message is None:
        message_queue.append([DateTime.now(), text])
    else:
        last_message.reply_text(text)
        if len(message_queue) > 0:
            last_message.reply_text("There were also some unread messages while you were away.")
            while len(message_queue) > 0:
                popped = message_queue.pop()
                last_message.reply_text(f"{popped[0]}\n\n{popped[1]}")


def last_received(message: Message):
    """Keeps track of where the last message came from so we can reply to it at any time."""
    global last_message
    last_message = message


def command_handler(update, context):
    """"""
    last_received(update.message)

    clean_text = update.message.text.strip().lower()
    if clean_text in ['hi', 'hellow', 'howdee']:
        # Greet the user
        send_message("Well, howdee partner!")
    elif clean_text in ['temp', 'rh', 'data']:
        # User requested details
        ada_rh, ada_temp = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if None in [ada_rh, ada_temp]:
            send_message("The sensor is currently down.")
        else:
            if clean_text == "temp":
                send_message(f"The current {THRESHOLD_TEMP[2].lower()} is {ada_temp:.2f}{THRESHOLD_TEMP[3]}.")
            if clean_text == "temp":
                send_message(f"The current {THRESHOLD_RH[2].lower()} is {ada_rh:.2f}{THRESHOLD_RH[3]}.")
            else:
                send_message(
                    f"The current sensor reading is {ada_temp:.2f}{THRESHOLD_TEMP[3]} at {ada_rh:.2f}{THRESHOLD_RH[3]}."
                )
    elif clean_text == "ping":
        send_message(f"pong")
    else:
        send_message(f"I don't know what to do with '{clean_text}'.")


#----------------------------------------------------------------------------------------------------------------------
def monitor_threshold(bound, value, current_status):
    """

    :param bound:
    :param value:
    :param current_status:
    :return:
    """
    result = NORMAL
    if (current_status != NORMAL) and (bound[0] <= value <= bound[1]):
        send_message(f"{bound[2]} has re-entered normal range. It's currently {value}{bound[3]}")
    elif bound[0] > value:
        # Value too low
        result = LOW
        if current_status != LOW:
            # Status changed
            send_message(
                f"{bound[2]} too low! Current value is {value:.2f}{bound[3]} (threshold: {bound[0]:.2f}{bound[3]})"
            )
    elif value > bound[1]:
        # Temp too high
        result = HIGH
        if current_status != HIGH:
            # Status changed
            send_message(
                f"{bound[2]} too high! Current value is {value:.2f}{bound[3]} (threshold: {bound[1]:.2f}{bound[3]})"
            )
    else:
        pass  # We should never end up here

    return result


def monitor_sensor(old_status, new_status):
    """

    :param old_status:
    :param new_status:
    :return:
    """
    if old_status != new_status:
        if new_status:
            send_message(f"Sensor has gone back online.")
        else:
            send_message(f"Sensor has gone offline.")

    return new_status


#----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main
    """
    # Init bot
    updater = Updater(TELEGRAM_BOT_API_KEY, use_context=True)

    # Add handler(s)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, command_handler))

    # Start bot
    updater.start_polling()
    try:
        # Monitor temp
        status_temp = 0
        status_rh = 0
        sensor_online = True
        while True:
            # Poll the sensor
            ada_rh, ada_temp = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

            # Check the data
            sensor_online = monitor_sensor(sensor_online, None not in [ada_rh, ada_temp])
            if sensor_online:
                status_temp = monitor_threshold(THRESHOLD_TEMP, ada_temp, status_temp)
                status_rh = monitor_threshold(THRESHOLD_RH, ada_rh, status_rh)

            time.sleep(5)
    except KeyboardInterrupt:
        pass
        #updater.idle()


#----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
