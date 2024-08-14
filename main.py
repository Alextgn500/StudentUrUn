immutable_var=(1,'Hello',0.125, True)
print('tuple_immutable_var:',immutable_var)
#immutable_var[0]=2
#print(immutable_var)
mutable_list = [1,2,3,4,5]
mutable_list[0]=55
mutable_list.append('59')
mutable_list.remove(2)
print(mutable_list)