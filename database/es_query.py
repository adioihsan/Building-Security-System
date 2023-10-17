from database import connection

es = connection.get_connection.elastic_search
def match_face_vector(face_embedding,index_name = "face_biometric"):
    query = {
        "size": 1,
        "query": {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                #"source": "cosineSimilarity(params.queryVector, 'title_vector') + 1.0",
                "source": "1 / (1 + l2norm(params.queryVector, 'biometric_vector'))", #euclidean distance
                "params": {
                    "queryVector": list(face_embedding)
                }
            }
        }
    }}
    return es.search(index=index_name, body=query)

def add_face_vector(face_embedding,private_id,full_name,index_name = "face_biometric"):
    try:
        doc = {"biometric_vector": face_embedding,"private_id":private_id, "full_name": full_name}
        es.index(index=index_name, body=doc)
        return (True,"User added","")
    except Exception as ex:
        print("ERROR: ",ex)
        return (False,"Server Error","")
