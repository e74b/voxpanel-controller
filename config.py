import os
import sys
import dotenv
import logging

dotenv.load_dotenv()

logger = logging.getLogger("config")

if "RMQ_URL" not in os.environ:
    logger.error("no `RMQ_URL` (rabbitmq url) environment variable is specified.")
    sys.exit(1)
RMQ_URL = os.environ["RMQ_URL"]

if "POSTGRES_URL" not in os.environ:
    logging.error("no `POSTGRES_URL` environment variable is specified")
    sys.exit(1)
POSTGRES_URL = os.environ["POSTGRES_URL"]

generated_token = None
if "JWT_SECRET" not in os.environ:
    logging.info("no `JWT_SECRET` environment vairable present, will generate new token")
    import secrets
    generated_token = secrets.token_hex(32)
    dotenv.set_key("./.env", "JWT_SECRET", generated_token)
JWT_SECRET = os.environ.get("JWT_SECRET", generated_token)

# Queue and Exchange names
RMQ_LOG_EXCHANGE = "logs"
RMQ_CONTROL_EXCHANGE = "control"
RMQ_SERVER_EXCHANGE = "server"
RMQ_AGENT_GLOBAL = "agent-global"
RMQ_SERVER_MSG_TTL = 30_000
RMQ_AGENT_MSG_TTL = 5_000
