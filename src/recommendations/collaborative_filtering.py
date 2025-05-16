from neo4j import GraphDatabase
from tabulate import tabulate


class ProductRecommender:

    def __init__(self, driver):
        self.driver = driver

    def get_user_based_recommendations(self, target_user_id, top_n=5):
        similarity_query = """
        CALL gds.nodeSimilarity.stream(
          'userProductGraph',
          {
            topK: 10,
            similarityCutoff: 0.1
          }
        )
        YIELD node1, node2, similarity
        WHERE gds.util.asNode(node1).id = $user_id
        RETURN
          gds.util.asNode(node2).id AS similar_user,
          similarity
        ORDER BY similarity DESC
        LIMIT 20;
        """

        recommendation_query = """
        MATCH (target:User {id: $user_id})
        WITH target
        MATCH (similar:User)-[:PURCHASED]->(p:Product)
        WHERE similar.id IN $similar_users AND NOT (target)-[:PURCHASED]->(p)
        RETURN p.name AS recommended_product, COUNT(*) AS frequency
        ORDER BY frequency DESC
        LIMIT $top_n
        """

        with self.driver.session() as session:
            # Step 1: Tìm các user tương tự
            similar_users_result = session.run(similarity_query, user_id=int(target_user_id))
            similar_user_ids = [record["similar_user"] for record in similar_users_result]

            if not similar_user_ids:
                print("\n⚠️ Không tìm thấy người dùng tương tự.")
                return []


            result = session.run(recommendation_query, user_id=int(target_user_id), similar_users=similar_user_ids,
                                 top_n=top_n)

            table_data = []
            records = []
            for i, record in enumerate(result, 1):
                name = record.get("recommended_product", "Unknown")
                freq = record.get("frequency", 0)
                table_data.append([i, name, freq])
                records.append({"product": name, "score": freq})

            print("\n👥 User-Based Collaborative Recommendations (GDS-Based):")
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
