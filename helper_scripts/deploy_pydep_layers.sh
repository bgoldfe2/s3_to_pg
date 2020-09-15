echo $(aws lambda publish-layer-version --layer-name "aws-pg-layer" \
--description "Library that enables psycopg2" \
--compatible-runtime "python3.8" \
--zip-file fileb://pg-layer/aws-pg-layer.zip)