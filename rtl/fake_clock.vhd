library IEEE;
use IEEE.std_logic_1164.all;  
use IEEE.numeric_std.all;     


entity fake_clock is

    port 
    (     
        clk1x               : in  std_logic;  
        clk2x               : in  std_logic;  
        clk3x               : in  std_logic;
        clk2xIndex          : out std_logic;
        clk3xIndex          : out std_logic
    );
end entity;

architecture arch of fake_clock is 
    signal clk1xToggle      : std_logic := '0';
    signal clk1xToggle2x    : std_logic := '0';
    signal clk1xToggle3x    : std_logic := '0';
    signal clk1xToggle3X_1  : std_logic := '0';
begin

-- clock index
    process (clk1x)
    begin
    if rising_edge(clk1x) then
    clk1xToggle <= not clk1xToggle;
    end if;
    end process;

    process (clk2x)
    begin
        if rising_edge(clk2x) then
            clk1xToggle2x <= clk1xToggle;
            clk2xIndex    <= '0';
            if (clk1xToggle2x = clk1xToggle) then
                clk2xIndex <= '1';
            end if;
        end if;
    end process;

    process (clk3x)
    begin
        if rising_edge(clk3x) then
            clk1xToggle3x   <= clk1xToggle;
            clk1xToggle3X_1 <= clk1xToggle3X;
            clk3xIndex    <= '0';
            if (clk1xToggle3X_1 = clk1xToggle) then
                clk3xIndex <= '1';
            end if;
        end if;
    end process;

end architecture;