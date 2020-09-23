echo $(aws lambda publish-layer-version --layer-name "aws-pg-layer2" \
--description "Library that enables psycopg2" \
--compatible-runtime "python3.8" \
--zip-file fileb://helper_scripts/pg_layer/aws-pg-layer.zip)