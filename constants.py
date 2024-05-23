TABLE_OPTIONS = [
    {'label': 'Covid19 - Global', 'value': 'covid_global'},
    {'label': 'Covid19 - Romania', 'value': 'covid_romania'},
    {'label': 'Covid19 - Timisoara', 'value': 'covid19_tm'},
    {'label': 'Status', 'value': 'status'},
]

COLUMN_NAME_MAPPING = {
    'CASES': 'Cases',
    'DEATHS': 'Deaths',
    'SUM_DEATHS': 'Total Deaths',
    'DAILY_DEATHS': 'Daily Deaths',
    'SUM_CASES': 'Total Cases',
    'DAILY_CASES': 'Daily Cases',
    'SUM_HOSPITAL': 'Total Hospitalizations',
    'MASK_USE': 'Mask use Rate',
    'SUM_VAC': 'Total Vaccinations',
    'SUM_FULL_VAC': 'Total Full Vaccinations',
    'HOSPITAL_CAPACITY': 'Total Hospital Capacity',
    'ICU_CAPACITY': 'Total ICU Capacity',
    'CURR_HOSP_OCC': 'Hospital Fill Rate',
    'CURR_ICU_OCC': 'ICU Fill Rate',
    'INFECTION_FATALITY': 'Infection Fatality Risk',
    'covid_global': 'Covid19 Global',
    'covid_romania': 'Covid19 Romania',
    'TOTAL_DEATHS': 'Total Deaths',
    'TOTAL_CASES': 'Total Cases',
    'TOTAL_RECOVERED': 'Total of Recovered',
    'DAILY_RECOVERED': 'Daily Recovered',
    'TOTAL_HOSPITALIZATIONS': 'Total Hospitalizations',
    'DAILY_HOSPITALIZATIONS': 'Daily Hospitalizations',
    'TOTAL_VACCINATIONS': 'Total Vaccinations',
    'DAILY_VACCINATIONS': 'Daily Vaccinations',
    'CURRENT_HOSP_OCCUPANCY': 'Hospital Fill Rate',
    'CURRENT_ICU_OCCUPANCY': 'ICU Fill Rate',
    'REGISTERED': 'Cases Registered',
    'TIMESTAMP': 'Over Time',
    'DAY_INCREMENT': 'Over Time'
}

SIMULATION_LABELS = {
    'numberOfAgentsParam': 'Number of Agents: ',
    'numberOfSickAtStartParam': 'Number Sick at Start: ',
    'simPeriodParam': 'Simulation Period (months): ',
    'standardIncubationTimeDiseaseParam': 'Incubation Time (days): ',
    'chanceToTransmitDiseaseParam': 'Transmission Chance: ',
    'healingTimeDiseaseParam': 'Healing Time (days): ',
    'initialChanceToHealParam': 'Initial Immunity (Probability of agents to have natural immunity to the Disease): ',
    'initialChanceToKillParam': 'Initial Lethality (Probability of Disease to have a higher lethality): ',
    'chanceForAsymptomaticParam': 'Asymptomatic Chance (Probability of asymptomatic agents): ',
    'chanceToGoOutParam': 'Chance to Go Out (Probability of an agent to leave their home): ',
    'chanceToSelfQuarantineParam': 'Chance to Self-Quarantine (Probability of agents to self-quarantine when starting to have symptoms): ',
    'agentsAtCentralLocation_atSameTimeParam': 'Agents at a Central Location (at the same time): ',
    'maskDistributionTimeParam': 'Mask distribution time (days): ',
    'maskCooldownTimeParam': 'Mask removal time (days): ',
    'maskUse': 'Mask Use Enforced: ',
    'vaccineDistributionTimeParam': 'Vaccine distribution time (days): ',
    'vaccineEnforced': 'Vaccine Enforced: '
}


BY_DATE = 'DATE_ID'
BY_ID = 'DAY_INCREMENT'
