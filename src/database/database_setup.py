from neo4j import GraphDatabase


class DatabaseSetup:
    def __init__(self):
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "123@123@"
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT user_id_unique IF NOT EXISTS
                FOR (u:User)
                REQUIRE u.id IS UNIQUE
            """)

            session.run("""
                CREATE CONSTRAINT product_id_unique IF NOT EXISTS
                FOR (p:Product)
                REQUIRE p.id IS UNIQUE
            """)

            session.run("""
                CREATE CONSTRAINT category_name_unique IF NOT EXISTS
                FOR (c:Category)
                REQUIRE c.name IS UNIQUE
            """)

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")