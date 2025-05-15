from neo4j import GraphDatabase
from tabulate import tabulate


class ProductRecommender:

    def __init__(self, driver):
        self.driver = driver

    def get_user_based_recommendations(self, target_user_id, top_n=5):
        query = """
        MATCH (target:User {id: $user_id})-[:PURCHASED]->(p:Product)
        MATCH (similar:User)-[:PURCHASED]->(p)
        WHERE target <> similar
        WITH target, similar, COUNT(*) AS shared
        ORDER BY shared DESC
        LIMIT 20

        MATCH (similar)-[:PURCHASED]->(recommended:Product)
        WHERE NOT (target)-[:PURCHASED]->(recommended)
        RETURN recommended.name AS recommended_product, COUNT(*) AS frequency
        ORDER BY frequency DESC
        LIMIT $top_n
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=int(target_user_id), top_n=top_n)

            table_data = []
            records = []

            for i, record in enumerate(result, 1):
                name = record.get("recommended_product", "Unknown")
                freq = record.get("frequency", 0)
                table_data.append([i, name, freq])
                records.append({"product": name, "score": freq})

            # In đẹp:
            print("\n👥 User-Based Collaborative Recommendations:")
            print(tabulate(table_data, headers=["No.", "Product Name", "Frequency"], tablefmt="fancy_grid"))

            return records

    def get_category_based_recommendations(self, target_user_id, top_n=5):
        query = """
        MATCH (u:User {id: $user_id})-[:PURCHASED]->(:Product)-[:BELONGS_TO]->(c:Category)
        WITH u, c.name AS category, COUNT(*) AS cnt
        ORDER BY cnt DESC
        LIMIT 1

        MATCH (:Category {name: category})<-[:BELONGS_TO]-(p:Product)
        WHERE NOT (u)-[:PURCHASED]->(p)
        RETURN p.name AS recommended_product, category
        LIMIT $top_n
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=int(target_user_id), top_n=top_n)
            records = []

            table_data = []
            for i, record in enumerate(result, 1):
                product = record.get("recommended_product", "Unknown")
                category = record.get("category", "N/A")
                table_data.append([i, product, category])
                records.append({"product": product, "category": category})

            print("\n📂 Category-Based Recommendations:")
            print(tabulate(table_data, headers=["No.", "Product Name", "Category"], tablefmt="fancy_grid"))

            return records
