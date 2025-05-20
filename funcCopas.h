// CORES PRINT
#define PRETO "\033[38;2;0;0;0;48;2;256;256;256m"
#define VRMLO "\033[38;2;256;0;0;48;2;256;256;256m"
#define RESET "\033[0m"

// NAIPES
#define S  '♠'
#define P  '♣'
#define C  '♥'
#define O  '♦'

typedef struct {

    unsigned int num;
    unsigned char naipe;

} carta;
