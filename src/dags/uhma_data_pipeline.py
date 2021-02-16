import csv
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_sql import CloudSQLExportInstanceOperator

default_args = {
    "owner": "uhma",
    "start_date": datetime(2021, 2, 13),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "omar.saucedo@wizeline.com",
    "retries": 1,
    "retries_delay": timedelta(minutes=5),
}

with DAG(dag_id="uhma_data_pipeline",
        schedule_interval="@daily",
        default_args=default_args,
        catchup=False) as dag:
    
    export_body = {
        "exportContext": {
            "fileType": "CSV",
            "databases": [
                "uhma",
            ],
            "uri": "gs://uhma_test/uhma_export.csv",
            "csvExportOptions": {
                "selectQuery": """
                    SELECT 
                        COALESCE(v.beneficiario, 0) AS 'beneficiary', 
                        u.nombre AS 'name',
                        u.apellido_paterno AS 'last_name',
                        u.apellido_materno AS 'second_last_name',
                        CASE 
                            WHEN u.sexo = 0
                                THEN 'F'
                            ELSE 'M'
                        END AS 'gender',
                        COALESCE(STR_TO_DATE( 
                            CONCAT( u.nacimiento_dia, '/', u.nacimiento_mes, '/', u.nacimiento_anio ),
                            '%d/%m/%Y' 
                        ), 0) AS 'birthdate',
                        COALESCE(TIMESTAMPDIFF(
                            YEAR, 
                            STR_TO_DATE( 
                            CONCAT( u.nacimiento_dia, '/', u.nacimiento_mes, '/', u.nacimiento_anio ),
                            '%d/%m/%Y' 
                            ), 
                            FROM_UNIXTIME(v.fecha_valoracion/1000, '%Y-%c-%d')
                        ), 0) AS 'age',
                        COALESCE(v.organizacion, 0) AS 'organization', 
                        COALESCE(v.peso, 0) AS 'weight',
                        COALESCE(v.estatura, 0) AS 'height',
                        COALESCE(v.presion_arterial_diastolica, 0) AS 'dbp', 
                        COALESCE(v.presion_arterial_sistolica, 0) AS 'sbp', 
                        COALESCE(v.indice_grasa, 0) AS 'fat_index',
                        COALESCE(v.frecuencia_cardiaca, 0) AS 'hr', 
                        COALESCE(v.glucosa, 0) AS 'glucose', 
                        COALESCE(v.colesterol, 0)  AS 'cholesterol', 
                        COALESCE(v.trigliceridos, 0)  AS 'triglycerides', 
                        COALESCE(v.proteinas, 0)  AS 'proteins', 
                        COALESCE(v.minerales, 0)  AS 'minerals', 
                        COALESCE(v.agua, 0)  AS 'water', 
                        COALESCE(v.imc, 0) AS 'bmi',
                        FROM_UNIXTIME(v.fecha_valoracion/1000, '%Y-%c-%d') AS 'date' 
                    FROM 
                        beneficiario_valoracion v
                    LEFT JOIN usuario u ON v.beneficiario = u.id 
                    WHERE 
                        v.fecha_valoracion > 0
                        AND v.peso BETWEEN 30 and 300
                        AND v.estatura > 100
                        AND v.frecuencia_cardiaca > 40
                        AND u.nombre IS NOT NULL
                        AND u.nacimiento_anio IS NOT NULL 
                        AND u.nacimiento_anio BETWEEN 1900 AND 2010
                        AND u.nacimiento_mes IS NOT NULL
                        AND u.nacimiento_mes BETWEEN 1 AND 12
                        AND u.nacimiento_dia IS NOT NULL
                        AND u.nacimiento_dia BETWEEN 1 AND 31;
                """
            },
        },
    }
    export_db_tables = CloudSQLExportInstanceOperator(
        task_id="export_db_tables",
        project_id="uhma-303820",
        body=export_body,
        instance="uhma",
        poke_interval=5,
        timeout=20,
    )
