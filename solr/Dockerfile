FROM ckan/ckan-solr:2.10-solr9

# Add the vector field type definition(s) and field(s)
# The default provided is meant to be used with Sentence Transformers' all-MiniLM-L6-v2 model
# For other models you will have to adjust the vectorDimension value

USER root

ENV SOLR_VECTOR_FIELD_DEFINITION '<fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="384" similarityFunction="cosine"/>'
ENV SOLR_VECTOR_FIELD '<field name="vector" type="knn_vector" indexed="true" stored="true"/>'

RUN sed -i "/<types>/a $SOLR_VECTOR_FIELD_DEFINITION" $SOLR_SCHEMA_FILE
RUN sed -i "/<fields>/a $SOLR_VECTOR_FIELD" $SOLR_SCHEMA_FILE

USER solr
