import warnings
warnings.filterwarnings('ignore')
import requests
import json
import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

ciclo = 'ele2022'
pleito = 545
now = datetime.datetime.now()
hour_now = int(str(datetime.datetime.now()).split(' ')[1].split(':')[0])
min_now = int(str(datetime.datetime.now()).split(' ')[1].split(':')[1])
waiting_sec = 120

def linear(x, a, b):
    return a*x + b

times = []
for hour in range(hour_now,22):
    if hour == hour_now:
        for minute in range(min_now, 60, 2):
            times.append('2022-10-30 {:02d}:{:02d}'.format(hour, minute))
    else:
        for minute in range(0, 60, 2):
            times.append('2022-10-30 {:02d}:{:02d}'.format(hour, minute))

results = {}
results['Time'] = []
results['Nº votos Lula'] = []
results['Nº votos Bolsonaro'] = []
results['Porcentagem Lula'] = []
results['Porcentagem Bolsonaro'] = []

while True:
    print('Updating...')
    print('\n')
    try:
        data = requests.get(
    f'https://resultados.tse.jus.br/oficial/{ciclo}/{pleito}/dados-simplificados/br/br-c0001-e000{pleito}-r.json')
        json_data = json.loads(data.content)
    except:
        print('Could not retrieve data now. Trying again in 30sec')
        time.sleep(30)

    candidato = []
    partido = []
    votos = []
    porcentagem = []
    for informacoes in json_data['cand']:
        if informacoes['seq'] == '1' or informacoes['seq'] == '2':
            candidato.append(informacoes['nm'])
            votos.append(informacoes['vap'])
            porcentagem.append(informacoes['pvap'])

    df_eleicao = pd.DataFrame(list(zip(candidato, votos, porcentagem)), columns = ['Candidato',
                                                                               'Nº votos',
                                                                               'Porcentagem'])

    print(df_eleicao)
    print('\n')
    
    print('Building DataFrame')
    results['Time'].append(f"2022-10-30 {str(datetime.datetime.now()).split(' ')[1].split(':')[0]}:{str(datetime.datetime.now()).split(' ')[1].split(':')[1]}")
    results['Nº votos Lula'].append(float(df_eleicao.loc[df_eleicao['Candidato'] == 'LULA']['Nº votos'].values[0]))
    results['Nº votos Bolsonaro'].append(float(df_eleicao.loc[df_eleicao['Candidato'] == 'JAIR BOLSONARO']['Nº votos'].values[0]))
    results['Porcentagem Lula'].append(df_eleicao.loc[df_eleicao['Candidato'] == 'LULA']['Porcentagem'].values[0])
    results['Porcentagem Bolsonaro'].append(df_eleicao.loc[df_eleicao['Candidato'] == 'JAIR BOLSONARO']['Porcentagem'].values[0])
    pd.DataFrame(results).to_csv(f"eleicao_2022_apuracao_tempo_real_comeco={hour_now}:{min_now}.csv")
    print('DataFrame saved.')
    print('\n')
    votos_total = np.array(results['Nº votos Lula']) + np.array(results['Nº votos Bolsonaro'])

    if len(pd.DataFrame(results)) > 5:
        print('Adjusting to data...')
        c, cov = curve_fit(linear, pd.DataFrame(results).index.values[len(results['Time'])-5:], (100*np.array(results['Nº votos Lula']/votos_total)[len(results['Time'])-5:]))
        c2, cov2 = curve_fit(linear, pd.DataFrame(results).index.values[len(results['Time'])-5:], (100*np.array(results['Nº votos Bolsonaro']/votos_total)[len(results['Time'])-5:]))
        print('\n')

    print('Plotting data')
    fig, ax = plt.subplots(figsize=(10,6))
    plt.plot(pd.to_datetime(results['Time'], format = '%Y-%m-%d %H:%M'), 100*np.array(results['Nº votos Lula'])/votos_total, color = 'crimson', lw = 3, label = 'Lula 13')
    plt.plot(pd.to_datetime(results['Time'], format = '%Y-%m-%d %H:%M'), 100*np.array(results['Nº votos Bolsonaro'])/votos_total, color = 'blue', lw = 3, label = 'Bolsonaro 22')
    if len(pd.DataFrame(results)) > 5:
        plt.plot(pd.todatetime.datetime(2022,10,30,16,0,0), datetime.datetime(2022,10,30,16,30,0),
                _datetime(times, format = '%Y-%m-%d %H:%M')[len(results['Time'])-5:],
        linear(np.array([i for i in range(len(times))])[len(results['Time'])-5:], *c),
        lw = 1, color = 'crimson', ls = '--', label = 'Tendência Lula')
        plt.plot(pd.to_datetime(times, format = '%Y-%m-%d %H:%M')[len(results['Time'])-5:],
        linear(np.array([i for i in range(len(times))])[len(results['Time'])-5:], *c2),
        lw = 1, color = 'blue', ls = '--', label = 'Tendência Bolsonaro')
    plt.xlabel('Hora', fontsize = 14)
    plt.ylabel('Porcentagem dos votos', fontsize = 14)
    plt.ylim(30, 70)
    plt.xlim(datetime.datetime(2022,10,30,17,0,0), datetime.datetime(2022,10,30,21,30,0))
    plt.xticks([datetime.datetime(2022,10,30,17,0,0), datetime.datetime(2022,10,30,17,30,0),
                datetime.datetime(2022,10,30,18,0,0), datetime.datetime(2022,10,30,18,30,0),
                datetime.datetime(2022,10,30,19,0,0), datetime.datetime(2022,10,30,19,30,0),
                datetime.datetime(2022,10,30,20,0,0), datetime.datetime(2022,10,30,20,30,0),
                datetime.datetime(2022,10,30,21,0,0), datetime.datetime(2022,10,30,21,30,0)],
                labels = ['17:00', '17:30', '18:00', '18:30', '19:00',
                '19:30', '20:00', '20:30', '21:00', '21:30'])
    plt.axhline(50, lw = 1, ls = '--', color = 'black')
    plt.legend(loc = 'upper left', fontsize = 12, ncol = 2)
    plt.title('Eleições Brasil 2022', fontsize = 20)
    plt.savefig('Apuracao_votos.png', dpi = 300, bbox_inches = 'tight')

    print(f"Waiting {(waiting_sec/60):.1f} min to update again - Hour = {str(datetime.datetime.now()).split(' ')[1].split(':')[0]}:{str(datetime.datetime.now()).split(' ')[1].split(':')[1]}")
    time.sleep(waiting_sec)
