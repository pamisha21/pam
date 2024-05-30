
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.util.*;

public class ChessGame extends JFrame {

    private static final int BOARD_SIZE = 8;
    private static final int CELL_SIZE = 80;
    private Piece[][] board;
    private boolean whiteTurn = true;
    private JButton saveButton, loadButton, newGameButton, showRulesButton;
    private JTextField filenameField;

    public ChessGame() {
        setTitle("Chess");
        setSize(800, 800);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        JPanel boardPanel = new JPanel(new GridLayout(BOARD_SIZE, BOARD_SIZE));
        board = new Piece[BOARD_SIZE][BOARD_SIZE];
        initializeBoard(boardPanel);

        JPanel controlPanel = new JPanel();
        filenameField = new JTextField(10);
        saveButton = new JButton("Save Game");
        loadButton = new JButton("Load Game");
        newGameButton = new JButton("New Game");
        showRulesButton = new JButton("Show Rules");

        saveButton.addActionListener(e -> saveGame());
        loadButton.addActionListener(e -> loadGame());
        newGameButton.addActionListener(e -> newGame(boardPanel));
        showRulesButton.addActionListener(e -> showRules());

        controlPanel.add(new JLabel("Filename:"));
        controlPanel.add(filenameField);
        controlPanel.add(saveButton);
        controlPanel.add(loadButton);
        controlPanel.add(newGameButton);
        controlPanel.add(showRulesButton);

        add(boardPanel, BorderLayout.CENTER);
        add(controlPanel, BorderLayout.SOUTH);
    }

    private void initializeBoard(JPanel boardPanel) {
        boardPanel.removeAll();
        board = createBoard();
        for (int y = 0; y < BOARD_SIZE; y++) {
            for (int x = 0; x < BOARD_SIZE; x++) {
                JPanel cell = new JPanel(new BorderLayout());
                cell.setBackground((y + x) % 2 == 0 ? Color.WHITE : Color.GRAY);
                if (board[y][x] != null) {
                    JLabel pieceLabel = new JLabel(board[y][x].getSymbol(), SwingConstants.CENTER);
                    pieceLabel.setFont(new Font("Segoe UI Symbol", Font.PLAIN, CELL_SIZE / 2));
                    cell.add(pieceLabel, BorderLayout.CENTER);
                }
                cell.setBorder(BorderFactory.createLineBorder(Color.BLACK));
                int finalY = y;
                int finalX = x;
                cell.addMouseListener(new MouseAdapter() {
                    @Override
                    public void mouseClicked(MouseEvent e) {
                        handleCellClick(finalY, finalX, boardPanel);
                    }
                });
                boardPanel.add(cell);
            }
        }
        boardPanel.revalidate();
        boardPanel.repaint();
    }

    private Piece[][] createBoard() {
        Piece[][] board = new Piece[BOARD_SIZE][BOARD_SIZE];
        String pieceOrder = "RNBQKBNR";
        for (int i = 0; i < BOARD_SIZE; i++) {
            board[0][i] = new Piece('b', pieceOrder.charAt(i));
            board[1][i] = new Piece('b', 'P');
            board[6][i] = new Piece('w', 'P');
            board[7][i] = new Piece('w', pieceOrder.charAt(i));
        }
        return board;
    }

    private void handleCellClick(int y, int x, JPanel boardPanel) {
        // Implement move handling here, similar to how you handle it in Python
        System.out.println("Cell clicked: " + y + ", " + x);
    }

    private void saveGame() {
        String filename = filenameField.getText().trim();
        if (filename.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter a filename.");
            return;
        }
        try (PrintWriter out = new PrintWriter(filename + ".txt")) {
            for (int y = 0; y < BOARD_SIZE; y++) {
                for (int x = 0; x < BOARD_SIZE; x++) {
                    out.print(board[y][x] == null ? " " : board[y][x]);
                    out.print(",");
                }
                out.println();
            }
            out.println(whiteTurn ? "w" : "b");
            JOptionPane.showMessageDialog(this, "Game saved successfully.");
        } catch (FileNotFoundException e) {
            JOptionPane.showMessageDialog(this, "Error saving game.");
        }
    }

    private void loadGame() {
        String filename = filenameField.getText().trim();
        if (filename.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter a filename.");
            return;
        }
        try (Scanner in = new Scanner(new File(filename + ".txt"))) {
            for (int y = 0; y < BOARD_SIZE; y++) {
                String[] line = in.nextLine().split(",");
                for (int x = 0; x < BOARD_SIZE; x++) {
                    board[y][x] = line[x].equals(" ") ? null : new Piece(line[x]);
                }
            }
            whiteTurn = in.nextLine().equals("w");
            initializeBoard((JPanel) getContentPane().getComponent(0));
            JOptionPane.showMessageDialog(this, "Game loaded successfully.");
        } catch (FileNotFoundException e) {
            JOptionPane.showMessageDialog(this, "Error loading game.");
        }
    }

    private void newGame(JPanel boardPanel) {
        board = createBoard();
        whiteTurn = true;
        initializeBoard(boardPanel);
    }

    private void showRules() {
        String rules = """
                RULES OF CHESS:
                1. Each player starts with 16 pieces: 1 king, 1 queen, 2 rooks, 2 knights, 2 bishops, and 8 pawns.
                2. The objective is to checkmate your opponent's king, meaning the king is in a position to be captured (in "check") and cannot escape.
                3. Pawns can move forward one square, but capture diagonally.
                4. Knights move in an L-shape: two squares in one direction and then one square perpendicular.
                5. Bishops move diagonally, while rooks move horizontally or vertically.
                
                Enjoy playing Chess!
                """;
        JTextArea rulesArea = new JTextArea(rules);
        rulesArea.setWrapStyleWord(true);
        rulesArea.setLineWrap(true);
        rulesArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(rulesArea);

        JFrame rulesFrame = new JFrame("Rules of Chess");
        rulesFrame.setSize(400, 300);
        rulesFrame.add(scrollPane);
        rulesFrame.setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            ChessGame game = new ChessGame();
            game.setVisible(true);
        });
    }
}

class Piece {

    private char side; // 'w' for white, 'b' for black
    private char type; // 'P' for pawn, 'R' for rook, 'N' for knight, 'B' for bishop, 'Q' for queen, 'K' for king

    public Piece(char side, char type) {
        this.side = side;
        this.type = type;
    }

    public Piece(String serialized) {
        this.side = serialized.charAt(0);
        this.type = serialized.charAt(1);
    }

    public String getSymbol() {
        int offset = (side == 'w') ? 9812 : 9818;
        return String.valueOf((char) (offset + "KQRBNP".indexOf(type)));
    }

    @Override
    public String toString() {
        return "" + side + type;
    }
}
