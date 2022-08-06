# Pattern Matching Operators

| **Operator**                     |                                                                                                                                                                                                                                                          **Meaning**                                                                                                                                                                                                                                                           |
|:---------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| `${variable # pattern}`          |                                                                                                                                                                                                 If the pattern matches the beginning of the variable’s value, delete the shortest part that matches and return the rest.                                                                                                                                                                                                  |
| `${variable ## pattern}`         |                                                                                                                                                                                                  If the pattern matches the beginning of the variable’s value, delete the longest part that matches and return the rest.                                                                                                                                                                                                  |
| `${variable % pattern}`          |                                                                                                                                                                                                    If the pattern matches the end of the variable’s value, delete the shortest part that matches and return the rest.                                                                                                                                                                                                     |
| `${variable %% pattern}`         |                                                                                                                                                                                                     If the pattern matches the end of the variable’s value, delete the longest part that matches and return the rest.                                                                                                                                                                                                     |
| `${variable / pattern/string}`   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `${variable // pattern/string}`  |  The longest match to pattern in variable is replaced by string. In the first form, only the first match is replaced. In the second form, all matches are replaced. If the pattern is begins with a #, it must match at the start of the variable. If it begins with a %, it must match with the end of the variable. If string is null, the matches are deleted. If variable is @ or *, the operation is applied to each positional parameter in turn and the expansion is the resultant list.  |

Assume `path` has the value /home/cam/book/long.file.name

| **Expression** |                    **Result** |
|----------------|------------------------------:|
| `${path##/*/}` |                long.file.name |
| `${path#/*/}`  |       cam/book/long.file.name |
| `$path`        | /home/cam/book/long.file.name | 
| `${path%.*}`   |      /home/cam/book/long.file | 
| `${path%%.*}`  |           /home/cam/book/long | 
