import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
# from matplotlib import rcParams
# rcParams.update({'figure.autolayout': True})
# plt.style.use('ggplot')


class Patient():

    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.all_data = pd.read_csv('data/phq_cleaned.csv', index_col=[0])
        self.valid = self.check_valid_id()
        if self.valid:
            self.history = self.get_history()
            self.stats = self.get_patient_stats()

    def check_valid_id(self):
        return self.patient_id in self.all_data.patient_id.values

    def plot_progress(self):
        if self.valid:
            c_palette = sns.color_palette("ch:s=.25,rot=-.25")

            fig, ax = plt.subplots(figsize = (10, 5))
            ax.plot(self.history['date'], self.history['score'], color = c_palette[1])
            ax.set_xlim(self.history.date.min(), self.history.date.max())
            ax.set_ylim(-0.5, 22, 2)
            ax.axhline(y = 10, linestyle = 'dashed', color = 'k', label = 'further eval')
            ax.xaxis.set_tick_params(rotation=90)
            ax.set_title(f'Patient ID: {self.patient_id}', fontsize = 14)
            ax.set_xlabel('Date')
            ax.set_ylabel('GAD7 Assessment Score')
            ax.fill_between(range(len(self.history)), 10, 22, color = 'indianred', alpha = 0.1)

            initial, final, avg_change, total_change, pct_further_eval = tuple(self.stats.values())  
            ax.text(len(self.history) - 0.5, 7, f'Total Delta: {round(total_change, 1)}\
                    \n \n Avg Delta between Visits: {round(avg_change, 1)} \
                    \n \n Further Eval Req (% of visits): {round(pct_further_eval, 1)}%')

            plt.tight_layout()
            name = str(self.patient_id)
            fig.savefig('images/'+name+'.png')
            fig.show()
        else: 
            print(f'{self.patient_id} is an invalid patient id')
    
    def get_patient_stats(self):
        self.stats = dict()
        self.stats['initial_score'] = self.history['score'][self.history['num_visit']==1].item()
        self.stats['final_score'] = self.history.sort_values('date', ascending = False).head(1)['score'].item()
        self.stats['avg_delta'] = self.history.score.diff().mean() 
        self.stats['total_change'] = self.stats['final_score']- self.stats['initial_score']
        self.stats['pct_further_eval'] = 100 - (np.sum(self.history.score < 10 ) / len(self.history) * 100)
        return self.stats

    def print_patient_stats(self):
        for k in self.stats:
            print(f'{str(k)}: {round(self.stats[k], 1)}')

    def get_history(self):
        return self.all_data[self.all_data['patient_id']==self.patient_id].sort_values('date')

    def determine_risk(self):
        pass

    def determine_stability(self):
        pass

if __name__ == '__main__':
    patient = 1867
    patient = Patient(1867)
    patient.plot_progress()
    patient.print_patient_stats()
    