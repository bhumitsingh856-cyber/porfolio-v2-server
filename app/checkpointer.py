from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv
import os

load_dotenv()

pool = AsyncConnectionPool(
    conninfo=os.getenv("PTR_URL"),
    min_size=1,
    max_size=10,
    open=False,
    max_idle=300,  
    max_lifetime=3600, 
    num_workers=3,
    kwargs={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "connect_timeout": 10,
        "options": "-c statement_timeout=0",  # disable statement timeout for long streams
    },
    check=AsyncConnectionPool.check_connection,
)
checkpointer = None