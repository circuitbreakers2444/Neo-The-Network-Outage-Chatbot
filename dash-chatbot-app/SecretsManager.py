import os
from databricks.sdk import WorkspaceClient

class SecretsManager:
    def __init__(self):
        self.workspace_client = WorkspaceClient()
        self._set_env_vars()

    def _set_env_vars(self):
        os.environ["DATABRICKS_TOKEN_WS"] = self.workspace_client.dbutils.secrets.get(scope="neo_keys", key="databricks_ws_key")
        os.environ["MISTRAL_API_KEY"] = self.workspace_client.dbutils.secrets.get(scope="neo_keys", key="mistral_key")
        os.environ["OPENAI_API_KEY"] = self.workspace_client.dbutils.secrets.get(scope="neo_keys", key="openai_key")
        os.environ["OPENWEATHERMAP_API_KEY"] = self.workspace_client.dbutils.secrets.get(scope="neo_keys", key="openweathermap_key")
