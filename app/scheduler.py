import gasprices
import time
import datetime
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

def main():
    while True:
        try:
            strid = "142028"
            gasprices.insert_gasprice(strid)
            logging.info(f"Script ran at: {datetime.datetime.now()}")
        except Exception as e:
            logging.error(f"Error occurred: {e}")
        finally:
            time.sleep(14400) 

if __name__ == "__main__":
    main()