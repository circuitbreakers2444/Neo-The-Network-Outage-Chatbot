import pandas as pd

class DataLoader:
    def __init__(self):
        self.df_outages = pd.read_csv("./data/planned_outages.csv")
        self.df_postcodes = pd.read_csv("./data/postcodes_suburb.csv")
        self.unplanned_outage_data = pd.read_csv('./data/past_electricity_outages_unplanned.csv')
        self.overall_avg_outage = self.unplanned_outage_data['Outage_Hours'].mean()
        self._process_data()

    def _process_data(self):
        self.df_outages['outage_start_date_time'] = pd.to_datetime(self.df_outages['outage_start_date_time'])
        self.df_outages['outage_end_date_time'] = pd.to_datetime(self.df_outages['outage_end_date_time'])
        self.df_outages['Postcode'] = self.df_outages['Postcode'].astype(str)
        self.df_postcodes['Postcode'] = self.df_postcodes['Postcode'].astype(str)
