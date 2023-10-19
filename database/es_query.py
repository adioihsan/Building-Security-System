from database import connection

es = connection.elastic_search
def match_face_vector(face_embedding,index_name = "face_biometric_512"):
    try:
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
    except Exception as ex:
        print("ERRO: Cant match the face vector. Cause",ex)
        raise Exception

def add_face_vector(face_embedding,private_id,full_name,index_name = "face_biometric_512"):
    try:
        doc = {"biometric_vector": face_embedding,"private_id":private_id, "full_name": full_name}
        es.index(index=index_name, body=doc)
        return (True,"User added","")
    except Exception as ex:
        print("ERROR:Cant add face vectore. Cause: ",ex)
        return (False,"Server Error","")
    
def delete_face_vector(private_id,index_name = "face_biometric_512"):
    try:
        query = {
        "query": {
            "term": {"private_id": private_id}
            }
        }
        result = es.delete_by_query(index=index_name, body=query)
        is_deleted = result["deleted"] > 0
        if is_deleted: 
            return (True, "Face vector deleted","")
        else: 
            return(False,f"User with private Id:{private_id} not registered")
    except Exception as ex:
        print("ERROR : Cant delete face vector. Cause:",ex)
        return (False,"Server Error","")