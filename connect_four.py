import math
from tkinter.constants import FALSE, TRUE

def get_child_boards(player, board):
    """
    Generate a list of succesor boards obtained by placing a disc 
    at the given board for a given player
   
    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that will place a disc on the board
    board: the current board instance

    Returns
    -------
    a list of (col, new_board) tuples,
    where col is the column in which a new disc is placed (left column has a 0 index), 
    and new_board is the resulting board instance
    """
    res = []
    for c in range(board.cols):
        if board.placeable(c):
            tmp_board = board.clone()
            tmp_board.place(player, c)
            res.append((c, tmp_board))
    return res


def evaluate(player, board):
    """
    This is a function to evaluate the advantage of the specific player at the
    given game board.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the specific player
    board: the board instance

    Returns
    -------
    score: float
        a scalar to evaluate the advantage of the specific player at the given
        game board
    """
    adversary = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    # Initialize the value of scores
    # [s0, s1, s2, s3, --s4--]
    # s0 for the case where all slots are empty in a 4-slot segment
    # s1 for the case where the player occupies one slot in a 4-slot line, the rest are empty
    # s2 for two slots occupied
    # s3 for three
    # s4 for four
    score = [0]*5
    adv_score = [0]*5

    # Initialize the weights
    # [w0, w1, w2, w3, --w4--]
    # w0 for s0, w1 for s1, w2 for s2, w3 for s3
    # w4 for s4
    weights = [0, 1, 4, 24, 1000] #Small adjustment made to s3 weight which gives better expected answers

    # Obtain all 4-slot segments on the board
    seg = []
    invalid_slot = -1
    left_revolved = [
        [invalid_slot]*r + board.row(r) + \
        [invalid_slot]*(board.rows-1-r) for r in range(board.rows)
    ]
    right_revolved = [
        [invalid_slot]*(board.rows-1-r) + board.row(r) + \
        [invalid_slot]*r for r in range(board.rows)
    ]
    for r in range(board.rows):
        # row
        row = board.row(r) 
        for c in range(board.cols-3):
            seg.append(row[c:c+4])
    for c in range(board.cols):
        # col
        col = board.col(c) 
        for r in range(board.rows-3):
            seg.append(col[r:r+4])
    for c in zip(*left_revolved):
        # slash
        for r in range(board.rows-3):
            seg.append(c[r:r+4])
    for c in zip(*right_revolved): 
        # backslash
        for r in range(board.rows-3):
            seg.append(c[r:r+4])
    # compute score
    for s in seg:
        if invalid_slot in s:
            continue
        if adversary not in s:
            score[s.count(player)] += 1
        if player not in s:
            adv_score[s.count(adversary)] += 1
    reward = sum([s*w for s, w in zip(score, weights)])
    penalty = sum([s*w for s, w in zip(adv_score, weights)])
    return reward - penalty


def minimax(player, board, depth_limit):
    """
    Minimax algorithm with limited search depth.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go further before stopping
    max_player: boolean

    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    
    max_player = player
    min_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    placement = None
    DEPTH = depth_limit


###############################################################################
    def value(player, board, depth_limit):
       if depth_limit == 0 or board.terminal():
            if board.terminal() and player == max_player:       # The following (1)-(4), are slight augmentations of the evaluation function for edge cases
                                                            #  in which I found that the algorithm didnt work optimally under these scenarios
                  
                  if depth_limit == DEPTH - 1:
                    return evaluate(max_player,board)+100,None #(1)If placing piece during the current turn causes a win for max player: VERY GOOD
                  else:
                      return evaluate(max_player,board)+50,None #(2)If terminal for max player: GOOD
                      
                  
            elif board.terminal() and player == min_player:
                  
                  if depth_limit == DEPTH - 2: #(3)If placing piece causes terminal for a min player: VERY BAD 
                    return evaluate(max_player,board)-90,None
                  else:  
                    return evaluate(max_player,board)-50,None #(4)If terminal for a min player: BAD
                  
            else : 
                return evaluate(max_player,board),None #evaluate must be sent the correct player

       if DEPTH == depth_limit:
        return max_value(max_player, board, depth_limit) #I start by calling Max_value as the game tree always starts at MAX
            
       if player == max_player: 
           # print('Next is MIN')
            return min_value(min_player, board, depth_limit)
       else: 
           #print('Next is MAX' )
           return max_value(max_player, board, depth_limit)



    def max_value(player, board, depth_limit):
        maxv = -math.inf
        #bestmove = get_child_boards(player, board)[0][0]

        for col,b in get_child_boards(player, board):
        
         currv =  value(player, b, depth_limit-1)[0]
         if currv > maxv:
             maxv = currv
             bestmove = col

       # print('The best case is', maxv, 'with col number', bestmove)
        return maxv, bestmove



    
    def min_value(player, board, depth_limit): #max player wants to pick the max of min values
        minv = math.inf

        for col,b in get_child_boards(player, board):
            
         currv =  value(player, b, depth_limit-1)[0]
         if currv < minv:
             minv = currv
             bestmove = col


        #print('The best value is', minv, 'with col number', bestmove)
        return minv, bestmove

    
  #  score = value(player, board, depth_limit)
    
    placement = value(player,board,depth_limit)[1]
    

###############################################################################
    return placement


def alphabeta(player, board, depth_limit):
    """
    Minimax algorithm with alpha-beta pruning.

     Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go further before stopping
    alpha: float
    beta: float
    max_player: boolean


    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    max_player = player
    placement = None
    min_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    DEPTH = depth_limit

############################################################################### ALPHABETA
    def value(player, board, depth_limit, alpha, beta):
       if depth_limit == 0 or board.terminal():
            if board.terminal() and player == max_player:           # The following (1)-(4), are slight augmentations of the evaluation function for edge cases
                                                            #  in which I found that the algorithm didnt work optimally under these scenarios
                  
                  if depth_limit == DEPTH - 1:
                    return evaluate(max_player,board)+100,None #(1) If placing piece during the current turn causes a win for max player: VERY GOOD
                  else:
                       return evaluate(max_player,board)+50,None #(2) If terminal for max player: GOOD
                      
                  
            elif board.terminal() and player == min_player:
                  
                  if depth_limit == DEPTH - 2: #(3) If placing piece causes terminal for a min player: VERY BAD 
                    return evaluate(max_player,board)-90,None
                  else:  
                    return evaluate(max_player,board)-50,None #(4) If terminal for a min player: BAD
                  
            else : 
                return evaluate(max_player,board),None #evaluate must be sent the correct player

       if DEPTH == depth_limit:
        return max_value(max_player, board, depth_limit, alpha, beta) #I start by calling Max_value as the game tree always starts at MAX

       if player == max_player: 
          #  print('Next is MIN', min_player, max_player)
            return min_value(min_player, board, depth_limit, alpha, beta)
       else: 
         #  print('Next is MAX' , min_player, max_player)
           return max_value(max_player, board, depth_limit, alpha, beta)



    def max_value(player, board, depth_limit, alpha, beta):
        maxv = -math.inf
       

        for col,b in get_child_boards(player, board):
        
         currv =  value(player, b, depth_limit-1, alpha, beta)[0]
         if currv > maxv:
             maxv = currv
             bestmove = col
        
         alpha = max(alpha, maxv)
        
         if (alpha >= beta):   
           # print(alpha, beta)  
            break

        # print('The best case is', currv, 'with col number', col)
        return maxv, bestmove



    
    def min_value(player, board, depth_limit, alpha, beta): #max player wants to pick the max of min values
        minv = math.inf
        

        for col,b in get_child_boards(player, board):
            
         currv =  value(player, b, depth_limit-1, alpha, beta)[0]
         if currv < minv:
             minv = currv
             bestmove = col
         beta = min(beta, minv) 
         
         if (alpha >= beta): 
           # print(alpha, beta)   
            break   

        # print('The min value is', currv, 'with adv placing in col number', col)
        return minv, bestmove



    
    placement = value(player,board,depth_limit, -math.inf, math.inf)[1]
###############################################################################
    return placement


def expectimax(player, board, depth_limit):
    """
    Expectimax algorithm.
    We assume that the adversary of the initial player chooses actions
    uniformly at random.
    Say that it is the turn for Player 1 when the function is called initially,
    then, during search, Player 2 is assumed to pick actions uniformly at
    random.

    Parameters
    ----------
    player: board.PLAYER1 or board.PLAYER2
        the player that needs to take an action (place a disc in the game)
    board: the current game board instance
    depth_limit: int
        the tree depth that the search algorithm needs to go before stopping
    max_player: boolean

    Returns
    -------
    placement: int or None
        the column in which a disc should be placed for the specific player
        (counted from the most left as 0)
        None to give up the game
    """
    max_player = player
    placement = None
    expec_player = board.PLAYER2 if player == board.PLAYER1 else board.PLAYER1
    DEPTH = depth_limit # const to hold the INITIAL depth

############################################################################### EXPECTIMAX
    def value(player, board, depth_limit):
         if depth_limit == 0 or board.terminal():
             
            if board.terminal() and player == max_player:   # The following (1)-(4), are slight augmentations of the evaluation function for edge cases
                                                            #  in which I found that the algorithm didnt work optimally under these scenarios
                  if depth_limit == DEPTH - 1:
                    return evaluate(max_player,board)+100,None #(1) If placing piece during the current turn causes a win for max player: VERY GOOD
                  else:
                      return evaluate(max_player,board)+50,None #(2) If terminal for max player: GOOD
                      
                  
            elif board.terminal() and player == expec_player:
                  
                  if depth_limit == DEPTH - 2: #(3) If placing piece causes terminal for a min player: VERY BAD (not as bad as winning though!)
                    return evaluate(max_player,board)-90,None
                  else:  
                    return evaluate(max_player,board)-50,None #(4) If terminal for a min player: BAD
                  
            else : 
                return evaluate(max_player,board),None #evaluate must be sent the correct player which is always from the max players POV

         if DEPTH == depth_limit:
            return max_value(max_player, board, depth_limit) #I start by calling Max_value as the game tree always starts at MAX

         if player == max_player:   # If the previous was MAX then next is EXPEC
            #print('Next is EXPEC')
            return expec_value(expec_player, board, depth_limit)
         else: 
           #print('Next is MAX')     # If the previous was MAX then next is MIN
           return max_value(max_player, board, depth_limit)



    def max_value(player, board, depth_limit):
        maxv = -math.inf

        for col,b in get_child_boards(player, board):
        
         currv =  value(player, b, depth_limit-1)[0]
         if currv > maxv:
             maxv = currv
             bestmove = col
         
         
        #print('The best case is', maxv, 'with col number', bestmove)
        return maxv, bestmove


    
    def expec_value(player, board, depth_limit): #max player wants to pick the max of min values
        expecv = 0

        for col,b in get_child_boards(player, board):
            
         expecv += (1/7) * value(player, b, depth_limit-1)[0] # Proabilities are equal
     
        #print('The expected value is', expecv)
        return expecv, None
    
    placement = value(player,board,depth_limit)[1] 
###############################################################################
    return placement


if __name__ == "__main__":
    from game_gui import GUI
    import tkinter

    algs = {
        "Minimax": minimax,
        "Alpha-beta pruning": alphabeta,
        "Expectimax": expectimax
    }

    root = tkinter.Tk()
    GUI(algs, root)
    root.mainloop()
