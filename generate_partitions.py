import copy
import pandas as pd
from enum import Enum
import sys
import json
import random

#initialization
global_minimum = sys.maxsize
global_deviation = sys.maxsize
best_distribution = {}
output_file = 'output/distribution.json'
num_of_partitions = 10

#utility methods

def get_heurisitic_factor(ticks):
    global num_of_partitions
    max_possible = sum(ticks)
    min_possible = max(max(ticks), sum(ticks) // num_of_partitions)
    print(f"Answer Range: {min_possible:,} -> {max_possible:,}")
    heurisitic_factor = min_possible * 1.0001
    return heurisitic_factor

def printDistribution(distribution):
    global output_file
    f = open(output_file, "w")
    f.write(json.dumps(distribution))
    # for index, partition in enumerate(distribution['partitions']):
    #     print(f"Partition: {index}")
    #     print(f"Stocks: {partition['stocks']}")
    f.close()

def update_current_deviation(distribution, best_answer):
    deviation_ = 0
    for partition in distribution['partitions']:
        deviation_ += abs(partition['sum'] - best_answer)
    distribution['deviation'] = deviation_

def update_current_minimum(distribution):
    max_ = max([partition['sum'] for partition in distribution['partitions']])
    distribution['minimum'] = max_


# core logic
def getMiniumInCurrentDistribution(distribution, best_answer, disable_deviation = False):
    global global_minimum
    global global_deviation
    global best_distribution

    update_current_deviation(distribution, best_answer)
    update_current_minimum(distribution)
    if distribution['minimum'] < global_minimum:
        print(f"Current Minium Achieved: {distribution['minimum']:,}")
        global_minimum = distribution['minimum']
        best_distribution = copy.deepcopy(distribution)
        printDistribution(distribution)
    if distribution['minimum'] == global_minimum and not disable_deviation:
        # check for deviation if global_minimum is reached
        if distribution['deviation'] < global_deviation:
            # Even with the same minimum, 
            # there could be some partitions with more load than others,
            # so we can continue distributing until we reach minimum deviation
            print(f"Current Deviation Achieved: {distribution['deviation']:,}")
            global_deviation = distribution['deviation']
            best_distribution = copy.deepcopy(distribution)
            printDistribution(distribution)

def assign_partition(stock_ticks, current_index, distribution, threshold, best_answer):
    # print(f"Current Index: {current_index}")
    global num_of_partitions
    if current_index == len(stock_ticks):
        # this is true when all elements are assigned a partition
        # check if there are any empty partitions
        empty_partitions = [partition for partition in distribution['partitions'] if len(partition['elements']) == 0]
        if len(empty_partitions) == 0:
            # all partitions are filled
            # check if the current distribution is better than the current best partition
            getMiniumInCurrentDistribution(distribution, best_answer)
        return
    # calculate cost of selecting each partition and select the best cost
    for partition in range(0, num_of_partitions):
        # if by including the current element in the partition, the sum exceeds the threshold
        # then skip this branch of recursion tree for optimization as the possible answer
        # will always be greater than the threshold. Try putting the element in the next partition
        if distribution['partitions'][partition]['sum'] + stock_ticks[current_index]['volume'] > threshold:
            continue
        # include in current partition
        distribution['partitions'][partition]['elements'].append(stock_ticks[current_index]['volume'])
        distribution['partitions'][partition]['sum'] += stock_ticks[current_index]['volume']
        distribution['partitions'][partition]['stocks'].append(stock_ticks[current_index]['symbol'])
        # go inside the recursion tree
        assign_partition(stock_ticks, current_index + 1, distribution, threshold, best_answer)
        # exclude from current partition
        distribution['partitions'][partition]['elements'].pop()
        distribution['partitions'][partition]['sum'] -= stock_ticks[current_index]['volume']
        distribution['partitions'][partition]['stocks'].pop()


def generate_distribution(stock_ticks):
    global num_of_partitions
    distribution = {
        'deviation': sys.maxsize,
        'minimum': sys.maxsize,
        'partitions': [{'sum': 0, 'elements': [], 'stocks': []} for i in range(num_of_partitions)]
    }
    nums = [int(x['volume'])for x in stock_ticks]
    threshold = get_heurisitic_factor(nums)
    print(f"Skip all branches where any partition has sum more than {'{:,}'.format(threshold)}")
    best_answer = max(max(nums), sum(nums) // num_of_partitions)
    assign_partition(stock_ticks, 0, distribution, threshold, best_answer)

def run(df):
    stock_ticks = [
        {
            'symbol': df['symbol'][index],
            'volume': int(df['volume'][index]),
        } for index in range(0, len(df['volume']))
    ]
    stock_ticks = sorted(stock_ticks, key=lambda x: x['volume'], reverse=True)
    # Reverse the order of the stocks to get the best distribution faster,
    # but this step is not necessary
    N = len(stock_ticks)
    generate_distribution(stock_ticks)


# Driver Code
if __name__ == '__main__':
    stocks = pd.read_json('stocks.json')
    trading_volumes_df = pd.read_json('trading-volumes.json')
    print("\n\n")
    print(f"Distributing {len(trading_volumes_df)} stocks into {num_of_partitions} partitions")
    run(trading_volumes_df)