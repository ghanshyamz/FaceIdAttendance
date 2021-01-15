import psycopg2
import psycopg2.extras
#######################################
DB_HOST = "localhost"
DB_NAME = "FaceRecognition"
DB_USER = "postgres"
DB_PASS = "1234"
######################################
def connectToDatabase(): #returns connection and cursor to database
    conn = psycopg2.connect(dbname=DB_NAME,user=DB_USER,
                            password=DB_PASS,host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn,cur

def insertToDatabase(cur,name,time,date):
    cur.execute("INSERT INTO attendance (person_name,attendance_time,attendance_date) VALUES (%s,%s,%s)",(name,time,date))


def checkInDatabase(cur,name):
    personList = []
    cur.execute("SELECT * FROM attendance")
    for row in cur.fetchall():
        personList.append(row[0])
    if name in personList:
        return True
    else:
        return False

def deleteEntry(cur,name):
    cur.execute("DELETE FROM public.attendance WHERE person_name = %s",(name,))

