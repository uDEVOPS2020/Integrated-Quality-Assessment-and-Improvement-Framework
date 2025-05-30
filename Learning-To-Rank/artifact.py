import pandas
import os

# 0: MART (gradient boosted regression tree)
# 1: RankNet
# 2: RankBoost
# 3: AdaRank
# 4: Coordinate Ascent
# 6: LambdaMART
# 7: ListNet
# 8: Random Forests
# 9: Linear regression (L2 regularization)

print("Select the algorithm for prioritization:\n")
print("0: MART")
print("1: RankNet")
print("2: RankBoost")
print("3: AdaRank")
print("4: Coordinate Ascent")
print("6: LambdaMART")
print("7: ListNet")
print("8: Random Forests")



input1 = input()

if(input1==0):
    os.system("java -jar RankLib-2.12.jar -ranker "+0+" -train train.txt -epoch 5 -layer 2 -save model.txt")
elif (input1==6):
    os.system("java -jar RankLib-2.12.jar -ranker "+6+" -train train.txt -save model.txt -tree 30 -metric2T NDCG@10")
else :
    os.system("java -jar RankLib-2.12.jar -ranker "+input1+" -train train.txt -save model.txt")
    
os.system("java -jar RankLib-2.12.jar -load model.txt -rank test.txt -score score.txt")