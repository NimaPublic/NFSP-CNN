import psycopg2
import json

class SLMemory(object):
    def __init__(self,table):
        self.memory = []
        self.table = table

    def push(self, state_dict):
        state_dict = json.dumps(state_dict)
        self.memory.append(state_dict)

    def sample(self, batch_size):
        conn = psycopg2.connect("dbname=NFSP user=postgres password=postgres")
        cur = conn.cursor()
        cur.execute("SELECT to_json(STEP) FROM " + self.table + ' TABLESAMPLE SYSTEM_ROWS(%s)', [batch_size])
        docs = cur.fetchall()
        cur.close()
        conn.close()

        batch = []
        for doc in docs:
            doc = str(doc)
            doc = doc[1:]
            doc = doc[0:-2]
            doc = doc.replace('\'', '\"')
            doc = json.loads(doc)
            batch.append(doc)

        return batch

    def write_db(self):
        if self.memory.__len__() > 0:
            conn = psycopg2.connect("dbname=NFSP user=postgres password=postgres")
            cur = conn.cursor()

            for state in self.memory:
                cur.execute("INSERT INTO " + self.table + ' (step) VALUES(%s)', (state,))

            conn.commit()
            cur.close()
            conn.close()
        self.memory = []

    def __len__(self):
        return len(self.memory)