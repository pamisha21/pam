#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from tkinter import *
from time import asctime, localtime, time
from copy import deepcopy
from os import listdir

# Function to display the rules
def display_rules():
    rules = """
    RULES OF CHESS:
    1. Each player starts with 16 pieces: 1 king, 1 queen, 2 rooks, 2 knights, 2 bishops, and 8 pawns.
    2. The objective is to checkmate your opponent's king, meaning the king is in a position to be captured (in "check") and cannot escape.
    3. Pawns can move forward one square, but capture diagonally.
    4. Knights move in an L-shape: two squares in one direction and then one square perpendicular.
    5. Bishops move diagonally, while rooks move horizontally or vertically.
    

    Enjoy playing Chess!
    """
    # Create a new window to display the rules
    rules_window = Toplevel()
    rules_window.title("Rules of Chess")
    rules_text = Text(rules_window, wrap=WORD)
    rules_text.insert(END, rules)
    rules_text.pack(fill=BOTH, expand=True)

# Create the main window
master = Tk()
master.wm_title('Chess')

# Add a button to display the rules
rules_button = Button(master, text="Show Rules", command=display_rules)
rules_button.pack(pady=10)
# OPTIONS:
cellSize = 80
autoFill = True

class Piece(object):
    ''' Defines proporties of each piece '''
    def __init__(s,side='w', pType='P', moved=False):
        # Types: P=pawn, R=rook, N=knight, B=bishop, Q=queen, K=king
        s.pType, s.side, s.moved, s.sym = pType, side, moved, chr((9812 if side=='w' else 9818)+'KQRBNP'.find(pType))
    def __str__(s): return '%s#%s#%s'%(s.side, s.pType, int(s.moved)) # For writing to text file
    def promote(s,newType): s.pType, s.sym = newType, chr((9812 if s.side=='w' else 9818)+'KQRBNP'.find(newType))

def createBoard():
    ''' Creates a 2D array for the board and creates pieces in starting positions '''
    board, pieceOrder = [['' for x in range(8)] for y in range(8)], 'RNBQKBNR'
    for i in range(8):
        board[0][i] = Piece('b', pieceOrder[i])
        board[1][i] = Piece('b')
        board[7][i] = Piece(pType=pieceOrder[i])
        board[6][i] = Piece()
    return board

def unbindClick(*args):
    ''' Unbinds everything in args and removes their activefill '''
    global w
    for t in args:
        if t=='tiles':
            for y in range(8): # Tiles are unbound using tags they were bound with
                for x in range(8): w.tag_unbind('t'+str(y)+str(x), '<Button-1>')
        else:
            w.tag_unbind(t, '<Button-1>')
            w.itemconfig(t, activefill='')

def optionBind(c):
    ''' Binds the save, load and new options and gives them an activefill '''
    c.tag_bind('new', '<Button-1>', newGame)
    c.tag_bind('save', '<Button-1>', saveGame)
    c.tag_bind('load', '<Button-1>', loadGame)
    c.itemconfig('new', activefill='#806')
    c.itemconfig('save', activefill='#806')
    c.itemconfig('load', activefill='#806')

def newGame(e):
    ''' Resets board, turn, moveColor and enPassant '''
    global board, w, cellSize, turn, moveColor, enPassant, fbb, scb, smb
    board, turn, moveColor, enPassant = createBoard(), 1, 'w', 10
    unbindClick('w', 'b')
    fbb.set(0)
    scb.set(1)
    smb.set(0)
    print(asctime(localtime(time()))[11:19], '- New game started')
    drawBoard(w, cellSize, board)
    pieceBind(w)

def loadGame(e):
    ''' Loads in values for board, turn and moveColor from save file '''
    global board, w, cellSize, turn, moveColor, enPassant, textIn, fbb, scb, smb
    unbindClick('tiles', 'w', 'b')
    fileName = textIn.get() if textIn.get()!='' else 'Default save.txt'
    if fileName[-4:]!='.txt': fileName += '.txt'
    try:
        inFile = [line.strip() for line in open(fileName)]
        tempBoard = [[col for col in row.split(',')[:-1]] for row in inFile[:-5]]
        for y in range(8):
            for x in range(8):
                if tempBoard[y][x]!='':
                    d = tempBoard[y][x].split('#')
                    tempBoard[y][x] = Piece(d[0], d[1], bool(int(d[2])))
        turn, moveColor, enPassant, board = int(inFile[-6]), inFile[-5], int(inFile[-4]), deepcopy(tempBoard)
        fbb.set(int(inFile[-3]))
        scb.set(int(inFile[-2]))
        smb.set(int(inFile[-1]))
        print(asctime(localtime(time()))[11:19], '- Game loaded from \'%s\''%fileName)
    except FileNotFoundError: print(asctime(localtime(time()))[11:19], '- Save file \'%s\' not found'%fileName)
    except Exception: print(asctime(localtime(time()))[11:19], '- Save file \'%s\' is invalid'%fileName)
    drawBoard(w, cellSize, board)
    pieceBind(w)

def saveGame(e):
    ''' Writes values of board, turn and moveColor to a save file '''
    global board, turn, moveColor, enPassant, textIn, fbb, scb, smb
    fileName = textIn.get() if textIn.get()!='' else 'Default save.txt'
    if fileName[-4:]!='.txt': fileName += '.txt'
    outFile = open(fileName,'w')
    for x in board:
        for y in x: outFile.write(str(y)+',')
        outFile.write('\n')
    outFile.write(str(turn)+'\n'+moveColor+'\n'+str(enPassant)+'\n'+str(fbb.get())+'\n'+str(scb.get())+'\n'+str(smb.get()))
    outFile.close()
    print(asctime(localtime(time()))[11:19], '- Game saved to \'%s\''%fileName)

def drawBoard(c, cs, b):
    ''' Renders squares on canvas for board, and unicode chess symbols for each piece in their current positions '''
    global moveColor, turn, fbb, textIn, flipBoard, showCheck, showMoves
    c.delete(ALL)
    for y in range(8):
        for x in range(8):
            xLoc, yLoc = (20+7*cs-x*cs, 20+7*cs-y*cs) if fbb.get() and moveColor=='b' else (20+x*cs, 20+y*cs)
            c.create_rectangle(xLoc, yLoc, xLoc+cs, yLoc+cs, tags=('tile','t'+str(y)+str(x)), outline='', fill=('#fff' if(y+x)%2==0 else '#888'))
    c.create_rectangle(20, 20, 20+8*cs, 20+8*cs, fill="")
    for y in range(8):
        for x in range(8):
            xLoc, yLoc = (20+cs/2+7*cs-x*cs, 20+cs/2+7*cs-y*cs) if fbb.get() and moveColor=='b' else (20+cs/2+x*cs, 20+cs/2+y*cs)
            if b[y][x]!='': c.create_text(xLoc, yLoc, text=b[y][x].sym, tags=('piece', y, x, b[y][x].pType, b[y][x].side), font=('Segoe UI Symbol',int(cs/1.6)))

    c.create_text(40+8*cs, 20+cs/2, text=('Turn %s:'%turn), font=('Arial',int(cs/5)), anchor=W)
    c.create_text(40+8*cs, 20+cs, text=(('White' if moveColor=='w' else 'Black')+"'s move"), font=('Arial',int(cs/5)), anchor=W)
    c.create_text(40+8*cs, 20+cs*3/2, text='CHECK', font=('Arial',int(cs/5.5)), tags='check', anchor=W, fill='')

    c.create_text(40+8*cs, 20+cs*2, text='Pick promotion:', font=('Arial',int(cs/5.5)), anchor=W, tags='ps', fill='')
    c.create_text(40+8*cs, 20+cs*2.5, text=chr(9813 if moveColor=='w' else 9819), font=('Segoe UI Symbol',int(cs/3.2)), anchor=W, tags=('po','pQ'), fill='')
    c.create_text(40+8.5*cs, 20+cs*2.5, text=chr(9814 if moveColor=='w' else 9820), font=('Segoe UI Symbol',int(cs/3.2)), anchor=W, tags=('po','pR'), fill='')
    c.create_text(40+9*cs, 20+cs*2.5, text=chr(9815 if moveColor=='w' else 9821), font=('Segoe UI Symbol',int(cs/3.2)), anchor=W, tags=('po','pB'), fill='')
    c.create_text(40+9.5*cs, 20+cs*2.5, text=chr(9816 if moveColor=='w' else 9822), font=('Segoe UI Symbol',int(cs/3.2)), anchor=W, tags=('po','pN'), fill='')

    c.create_text(40+8*cs, 20+cs*3.5, text='Options:', font=('Arial',int(cs/5.5)), anchor=W)
    c.create_window(40+8*cs, 20+cs*4, window=flipBoard, anchor=W)
    c.create_window(40+8*cs, 20+cs*4.5, window=showCheck, anchor=W)
    c.create_window(40+8*cs, 20+cs*5, window=showMoves, anchor=W)

    c.create_text(40+8*cs, 20+cs*6, text='New game', font=('Arial',int(cs/5.5)), anchor=W, tags='new', activefill='#806')
    c.create_text(40+8*cs, 20+cs*6.5, text='Save game', font=('Arial',int(cs/5.5)), anchor=W, tags='save', activefill='#806')
    c.create_text(40+8*cs, 20+cs*7, text='Load game', font=('Arial',int(cs/5.5)), anchor=W, tags='load', activefill='#806')
    c.create_window(40+8*cs, 20+cs*7.5, window=textIn, tags='input', anchor=W, width=1.65*cs, height=1/3*cs)

def pieceBind(c):
    ''' Binds appropriate pieces and gives them an activefill, and displays check message '''
    global moveColor, scb
    unbindClick('tiles')
    c.tag_bind('w' if moveColor=='w' else 'b', '<Button-1>', pieceClick)
    c.itemconfig('w' if moveColor=='w' else 'b', activefill='#066')

    if scb.get():
        if hasNoMoves(moveColor, board):
            if inCheck(moveColor, board): w.itemconfig('check', fill='#A00', text='CHECKMATE')
            else: w.itemconfig('check', fill='#A00', text='STALEMATE')
        elif inCheck(moveColor, board): w.itemconfig('check', fill='#A00', text='CHECK')

def tileBind(c, *args):
    ''' Binds available tiles for a move to tileClick and gives them an activefill '''
    global moveColor, smb
    unbindClick('piece', 'w', 'b')
    c.itemconfig('b' if moveColor=='w' else 'w', state=DISABLED) # Clicks ignore pieces
    for t in args:
        c.itemconfig('t'+t, activefill='#066')
        if smb.get(): c.itemconfig('t'+t, fill='#C0E8DD' if (int(t[0])+int(t[1]))%2==0 else '#89A9A0')
        c.tag_bind('t'+t, '<Button-1>', tileClick)

def movePawn(y, x, color, board):
    ''' Calculates valid moves for a pawn '''
    global enPassant
    valid, sign = [], -1 if color=='w' else 1
    if board[y+sign][x]=='':
        valid.append(str(y+sign)+str(x))
        if not board[y][x].moved and board[y+2*sign][x]=='': valid.append(str(y+2*sign)+str(x))

    if x>0 and board[y+sign][x-1]!='':
        if board[y+sign][x-1].side!=color: valid.append(str(y+sign)+str(x-1))
    if x<7 and board[y+sign][x+1]!='':
        if board[y+sign][x+1].side!=color: valid.append(str(y+sign)+str(x+1))
    if y==(3 if color=='w' else 4) and abs(x-enPassant)==1: valid.append(str(y+(-1 if color=='w' else 1))+str(enPassant))
    return valid

def moveRook(y, x, color, board):
    ''' Calculates valid moves for a rook '''
    valid = []
    for r in range(4):
        for a in range(1,8) if r%2==0 else range(-1,-8,-1):
            if r<2: dx, dy = a, 0
            else: dx, dy = 0, a
            if x+dx in range(8) and y+dy in range(8):
                if board[y+dy][x+dx]!='':
                    if board[y+dy][x+dx].side!=color: valid.append(str(y+dy)+str(x+dx))
                    break
                else: valid.append(str(y+dy)+str(x+dx))
    return valid

def moveKnight(y, x, color, board):
    ''' Calculates valid moves for a knight '''
    shifts = (-1, 1, -2, 2)
    valid = [str(y+dy)+str(x+dx) for dy in shifts for dx in shifts if abs(dy)!=abs(dx) and y+dy in range(8) and x+dx in range(8)]
    valid = [x for x in valid if not(board[int(x[0])][int(x[1])]!='' and board[int(x[0])][int(x[1])].side==color)]
    return valid

def moveBishop(y, x, color, board):
    ''' Calculates valid moves for a bishop '''
    valid = []
    for r in range(4):
        for a in range(1,8) if r%2==0 else range(-1,-8,-1):
            if r<2: dx, dy = a, a
            else: dx, dy = a, -a
            if x+dx in range(8) and y+dy in range(8):
                if board[y+dy][x+dx]!='':
                    if board[y+dy][x+dx].side!=color: valid.append(str(y+dy)+str(x+dx))
                    break
                else: valid.append(str(y+dy)+str(x+dx))
    return valid

def moveQueen(y, x, color, board):
    ''' Calculates valid moves for a queen '''
    valid = []
    for r in range(8):
        for a in range(1,8) if r%2==0 else range(-1,-8,-1):
            if r<2: dx, dy = a, 0
            elif r<4: dx, dy = 0, a
            elif r<6: dx, dy = a, a
            else: dx, dy = a, -a
            if x+dx in range(8) and y+dy in range(8):
                if board[y+dy][x+dx]!='':
                    if board[y+dy][x+dx].side!=color: valid.append(str(y+dy)+str(x+dx))
                    break
                else: valid.append(str(y+dy)+str(x+dx))
    return valid

def moveKing(y, x, color, board):
    ''' Calculates valid moves for a king '''
    shifts = (-1, 1, 0)
    valid = [str(y+dy)+str(x+dx) for dy in shifts for dx in shifts if (dx!=0 or dy!=0) and y+dy in range(8) and x+dx in range(8)]
    valid = [v for v in valid if not(board[int(v[0])][int(v[1])]!='' and board[int(v[0])][int(v[1])].side==color)]

    if not board[y][x].moved:
        if (board[y][x+1],board[y][x+2])==('','') and board[y][x+3]!='' and not board[y][x+3].moved:
            if not (isThreatened(y,x,color,board) or isThreatened(y,x+1,color,board) or isThreatened(y,x+2,color,board)): valid.append(str(y)+str(x+2))
        if (board[y][x-1],board[y][x-2],board[y][x-3])==('','','') and board[y][x-4]!='' and not board[y][x-4].moved:
            if not (isThreatened(y,x,color,board) or isThreatened(y,x-1,color,board) or isThreatened(y,x-2,color,board)): valid.append(str(y)+str(x-2))
    return valid

def isThreatened(y, x, color, b):
    ''' Returns whether (y,x) is threatened '''
    global movePiece
    threatened = False
    for r in range(8):
        for a in range(1,8) if r%2==0 else range(-1,-8,-1):
            if r<2: dx, dy = a, 0
            elif r<4: dx, dy = 0, a
            elif r<6: dx, dy = a, a
            else: dx, dy = a, -a
            if x+dx in range(8) and y+dy in range(8):
                if b[y+dy][x+dx]!='':
                    if b[y+dy][x+dx].side!=color:
                        if r<4 and b[y+dy][x+dx].pType in 'QR': threatened = True
                        elif r>=4 and b[y+dy][x+dx].pType in 'QB': threatened = True
                        elif abs(a)==1 and b[y+dy][x+dx].pType=='K': threatened = True
                        elif (r==(5 if color=='w' else 4) or r==(6 if color=='w' else 7)) and abs(a)==1 and b[y+dy][x+dx].pType=='P': threatened = True
                    break

    shifts = (-1, 1, -2, 2)
    valid = [str(y+dy)+str(x+dx) for dy in shifts for dx in shifts if abs(dy)!=abs(dx) and y+dy in range(8) and x+dx in range(8)]
    for n in valid:
        if b[int(n[0])][int(n[1])]!='' and b[int(n[0])][int(n[1])].side!=color and b[int(n[0])][int(n[1])].pType=='N':
            threatened = True
            break
    return threatened

def inCheck(color, b):
    ''' Returns whether king is in check '''
    kingY, kingX = 9, 9
    for c in range(8):
        for d in range(8):
            if b[c][d]!='' and b[c][d].pType=='K' and b[c][d].side==color:
                kingY, kingX = c, d
                break
    return isThreatened(kingY, kingX, color, b)

def potentialCheck(y, x, nY, nX, color, board):
    ''' Returns whether moving piece at (y,x) to (nY,nX) causes king to be in check '''
    b = deepcopy(board)
    if b[y][x].pType=='P' and nX!=x and b[nY][nX]=='': b[nY+(1 if b[y][x].side=='w' else -1)][nX] = ''
    b[y][x], b[nY][nX] = '', b[y][x]
    return inCheck(color, b)

def calculateMove(y, x, pType, color, board):
    ''' Returns list of coordinates of tiles available for clicked piece to move '''
    valid = [movePawn, moveRook, moveKnight, moveBishop, moveQueen, moveKing]['PRNBQK'.find(pType)](y, x, color, board)
    return [v for v in valid if not potentialCheck(y, x, int(v[0]), int(v[1]), color, board)]

def hasNoMoves(color, board):
    ''' Returns whether color has no valid moves (checkmate or stalemate) '''
    noMoves = True
    for y in range(8):
        for x in range(8):
            if board[y][x]!='' and board[y][x].side==color:
                if len(calculateMove(y, x, board[y][x].pType, color, board))!=0:
                    noMoves = False
                    break
    return noMoves

def pieceClick(e):
    ''' Sets movePiece, calls function to calculate valid moves, and passes results to tileBind() '''
    global w, board, cellSize, movePiece
    tags = w.gettags(e.widget.find_closest(e.x, e.y))
    if tags[0]=='tile': # Clicking edge of piece finds tile instead
        tags = w.gettags(e.widget.find_overlapping(e.x-1, e.y-1, e.x+1, e.y+1)[1])
        w.itemconfig(e.widget.find_overlapping(e.x-1, e.y-1, e.x+1, e.y+1)[1], fill='#066')
    else: w.itemconfig(e.widget.find_closest(e.x, e.y), fill='#066')

    movePiece = (int(tags[1]), int(tags[2]))
    validTiles = calculateMove(int(tags[1]), int(tags[2]), tags[3], tags[4], board)
    if len(validTiles)==0: # Cancels move if no valid tiles exist
        drawBoard(w, cellSize, board)
        pieceBind(w)
    else: tileBind(w, *validTiles)

def tileClick(e):
    ''' Moves piece to clicked tile and executes special moves '''
    global w, board, movePiece, enPassant
    w.itemconfig(ALL, state=NORMAL)

    tags = w.gettags(e.widget.find_closest(e.x, e.y))
    if tags[0]=='piece': tags = w.gettags(e.widget.find_overlapping(e.x, e.y, e.x, e.y)[0])
    if (int(tags[1][1]),int(tags[1][2]))==(movePiece[0],movePiece[1]): tags = w.gettags(e.widget.find_overlapping(e.x, e.y+2, e.x, e.y-2)[1])

    if board[movePiece[0]][movePiece[1]].pType=='P' and abs(movePiece[0]-int(tags[1][1]))==2: enPassant = movePiece[1]
    else: enPassant = 10

    promotion = False
    if board[movePiece[0]][movePiece[1]].pType=='P' and tags[1][1] in ('0','7'): promotion = True
    elif board[movePiece[0]][movePiece[1]].pType=='K' and abs(movePiece[1]-int(tags[1][2]))==2:
        if int(tags[1][2])==2: board[movePiece[0]][0], board[movePiece[0]][3] = '', board[movePiece[0]][0]
        else: board[movePiece[0]][7], board[movePiece[0]][5] = '', board[movePiece[0]][7]
    elif board[movePiece[0]][movePiece[1]].pType=='P' and int(tags[1][2])!=movePiece[1] and board[int(tags[1][1])][int(tags[1][2])]=='':
        board[int(tags[1][1])+(1 if board[movePiece[0]][movePiece[1]].side=='w' else -1)][int(tags[1][2])] = ''

    board[movePiece[0]][movePiece[1]].moved = True
    board[movePiece[0]][movePiece[1]], board[int(tags[1][1])][int(tags[1][2])] = '', board[movePiece[0]][movePiece[1]]
    if promotion: promotionBind(int(tags[1][1]), int(tags[1][2]))
    else: advanceMove()

def promotionBind(y, x):
    ''' Shows promotion options and records promotion piece '''
    global promPiece, w, cellSize, board, flipBoard, showCheck
    drawBoard(w, cellSize, board)
    unbindClick('tiles', 'new', 'save', 'load')
    w.tag_bind('po', '<Button-1>', promotionClick)
    w.itemconfig('po', fill='#806', activefill='#C60')
    w.itemconfig('ps', fill='#806',)
    flipBoard.config(state=DISABLED)
    showCheck.config(state=DISABLED)
    showMoves.config(state=DISABLED)
    promPiece = (y, x)

def promotionClick(e):
    ''' Promotes pawn to selected piece and hides selection '''
    global w, cellSize, board, promPiece, flipBoard, showCheck
    w.tag_unbind('po', '<Button-1>')
    optionBind(w)
    board[promPiece[0]][promPiece[1]].promote(w.gettags(e.widget.find_closest(e.x, e.y))[1][1])
    flipBoard.config(state=NORMAL)
    showCheck.config(state=NORMAL)
    showMoves.config(state=NORMAL)
    advanceMove()

def advanceMove():
    ''' Begins the next color's move '''
    global w, cellSize, board, moveColor, turn
    moveColor = 'w' if moveColor=='b' else 'b'
    if moveColor=='w': turn += 1
    drawBoard(w, cellSize, board)
    pieceBind(w)

def inputFocusIn(e):
    ''' Clears text in input on selection '''
    ti = e.widget
    ti.config(bg='#BBF')
    ti.delete(0, END)

def inputFocusOut(e):
    ''' Restores text input state on deselection '''
    global v
    ti = e.widget
    ti.config(bg='#CCC')
    if ti.get()=='': v.set('Default save')
    elif ti.get()[-4:]!='.txt':
        v.set(v.get()+'.txt')
        ti.xview(END)

def inputKeyPress(e):
    ''' Sets filename and index for autofill, using text files in folder '''
    global v, w, textIn, fileName, selIndex
    if e.keysym=='Return':
        w.focus_set()
    elif e.char!='':
        saveFiles = sorted([f for f in listdir('.') if f[-4:]=='.txt'])
        for sf in saveFiles:
            if textIn.select_present(): match = v.get().rsplit(textIn.selection_get(),1)[0]+e.char
            else: match = v.get()+e.char
            if sf.startswith(match) and match!='':
                selIndex, fileName = len(match), sf
                textIn.unbind('<Key>')
                textIn.bind('<KeyRelease>', inputKeyRelease)
                textIn.config(state='readonly')
                break
        else: fileName = 'x'

def inputKeyRelease(e):
    ''' Autofills text input using values of fileName and selIndex '''
    global fileName, selIndex, textIn, v
    textIn.config(state=NORMAL)
    if fileName!='x':
        v.set(fileName)
        textIn.selection_range(selIndex, END)
        textIn.icursor(selIndex)
    textIn.bind('<Key>', inputKeyPress)
    textIn.unbind('<KeyRelease>')

def checkBox():
    ''' Redraws board when checkbox is clicked '''
    global w, cellSize, board
    drawBoard(w, cellSize, board)
    pieceBind(w)

# Sets up canvas, text input field and checkboxes
master = Tk()
master.wm_title('Chess')
w, v, fbb, scb, smb = Canvas(master, width=10*cellSize+40, height=8*cellSize+40, highlightthickness=0), StringVar(), IntVar(), IntVar(), IntVar()

textIn = Entry(w, font=('Arial', int(cellSize/7)), textvariable=v, bg='#CCC', bd=0, selectbackground='#77B', justify=CENTER, readonlybackground='#BBF')
textIn.bind('<FocusIn>', inputFocusIn)
textIn.bind('<FocusOut>', inputFocusOut)
if autoFill: textIn.bind('<Key>', inputKeyPress)
v.set('Default save')
w.bind('<Button-1>', lambda e: w.focus_set())

flipBoard = Checkbutton(w, font=('Arial', int(cellSize/7)), text='Flip board', variable=fbb, command=checkBox)
showCheck = Checkbutton(w, font=('Arial', int(cellSize/7)), text='Show check', variable=scb, command=checkBox)
showMoves = Checkbutton(w, font=('Arial', int(cellSize/7)), text='Show moves', variable=smb, command=checkBox)
showCheck.select()
w.pack()

# Creates global variables and draws board in initial setup
board, turn, moveColor, movePiece, promPiece, enPassant, fileName, selIndex = createBoard(), 1, 'w', (10, 10), (10, 10), 10, 'x', -1
drawBoard(w, cellSize, board)
print('\n[ SAVE LOG ]\n')

# Starts white's first turn
optionBind(w)
pieceBind(w)
mainloop()


# In[ ]:




