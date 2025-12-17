library IEEE;
use IEEE.std_logic_1164.all;  
use IEEE.numeric_std.all;     

entity cpu_mux is
    port
    (
        clk1x                : in  std_logic;
        clk2x                : in  std_logic;
        clk3x                : in  std_logic;
        ce                   : in  std_logic;
        reset_intern         : in  std_logic;

        cpuPaused            : in  std_logic;
        memMuxIdle           : out std_logic;

        loadExe              : in  std_logic;
        exe_initial_pc       : in  unsigned(31 downto 0);
        exe_initial_gp       : in  unsigned(31 downto 0);
        exe_load_address     : in  unsigned(31 downto 0);
        exe_file_size        : in  unsigned(31 downto 0);
        exe_stackpointer     : in  unsigned(31 downto 0);
        reset_exe            : out std_logic := '0';

        fastboot             : in  std_logic;
        PATCHSERIAL          : in  std_logic;
        TURBO_MEM            : in  std_logic;
        TURBO_COMP           : in  std_logic;
        TURBO_CACHE          : in  std_logic;
        TURBO_CACHE50        : in  std_logic;
        biosregion           : in  std_logic_vector(1 downto 0);

        ram_dataWrite        : out std_logic_vector(31 downto 0) := (others => '0');
        ram_dataRead32       : in  std_logic_vector(31 downto 0);
        ram_Adr              : out std_logic_vector(24 downto 0) := (others => '0');
        ram_be               : out std_logic_vector(3 downto 0) := (others => '0');
        ram_rnw              : out std_logic := '0';
        ram_ena              : out std_logic := '0';
        ram_cache            : out std_logic := '0';
        ram_done             : in  std_logic;

        -- GTE
        gte_busy             : in  std_logic;
        gte_readEna          : out std_logic;
        gte_readAddr         : out unsigned(5 downto 0);
        gte_readData         : in  unsigned(31 downto 0);
        gte_writeAddr        : out unsigned(5 downto 0);
        gte_writeData        : out unsigned(31 downto 0);
        gte_writeEna         : out std_logic; 
        gte_cmdData          : out unsigned(31 downto 0);
        gte_cmdEna           : out std_logic; 	

        cache_wr         	 : in  std_logic_vector(3 downto 0);
        cache_data       	 : in  std_logic_vector(31 downto 0);
        cache_addr       	 : in  std_logic_vector(7 downto 0);

        bios_memctrl         : in  unsigned(13 downto 0);

        ex1_memctrl          : in  unsigned(13 downto 0);
        --bus_exp1_addr        : out unsigned(22 downto 0); 
        --bus_exp1_dataWrite   : out std_logic_vector(7 downto 0);
        bus_exp1_read        : out std_logic;
        --bus_exp1_write       : out std_logic;
        bus_exp1_dataRead    : in  std_logic_vector(7 downto 0);

        bus_memc_addr        : out unsigned(5 downto 0); 
        bus_memc_dataWrite   : out std_logic_vector(31 downto 0);
        bus_memc_read        : out std_logic;
        bus_memc_write       : out std_logic;
        bus_memc_dataRead    : in  std_logic_vector(31 downto 0);

        bus_pad_addr         : out unsigned(3 downto 0); 
        bus_pad_dataWrite    : out std_logic_vector(31 downto 0);
        bus_pad_read         : out std_logic;
        bus_pad_write        : out std_logic;
        bus_pad_writeMask    : out std_logic_vector(3 downto 0);
        bus_pad_dataRead     : in  std_logic_vector(31 downto 0);

        bus_sio_addr         : out unsigned(3 downto 0); 
        bus_sio_dataWrite    : out std_logic_vector(31 downto 0);
        bus_sio_read         : out std_logic;
        bus_sio_write        : out std_logic;
        bus_sio_writeMask    : out std_logic_vector(3 downto 0);
        bus_sio_dataRead     : in  std_logic_vector(31 downto 0);

        bus_memc2_addr       : out unsigned(3 downto 0); 
        bus_memc2_dataWrite  : out std_logic_vector(31 downto 0);
        bus_memc2_read       : out std_logic;
        bus_memc2_write      : out std_logic;
        bus_memc2_dataRead   : in  std_logic_vector(31 downto 0);

        bus_irq_addr         : out unsigned(3 downto 0); 
        bus_irq_dataWrite    : out std_logic_vector(31 downto 0);
        bus_irq_read         : out std_logic;
        bus_irq_write        : out std_logic;
        bus_irq_dataRead     : in  std_logic_vector(31 downto 0);

        bus_dma_addr         : out unsigned(6 downto 0); 
        bus_dma_dataWrite    : out std_logic_vector(31 downto 0);
        bus_dma_read         : out std_logic;
        bus_dma_write        : out std_logic;
        bus_dma_dataRead     : in  std_logic_vector(31 downto 0);

        bus_tmr_addr         : out unsigned(5 downto 0); 
        bus_tmr_dataWrite    : out std_logic_vector(31 downto 0);
        bus_tmr_read         : out std_logic;
        bus_tmr_write        : out std_logic;
        bus_tmr_dataRead     : in  std_logic_vector(31 downto 0);

        cd_memctrl           : in  unsigned(13 downto 0);
        bus_cd_addr          : out unsigned(3 downto 0); 
        bus_cd_dataWrite     : out std_logic_vector(7 downto 0);
        bus_cd_read          : out std_logic;
        bus_cd_write         : out std_logic;
        bus_cd_dataRead      : in  std_logic_vector(7 downto 0);

        bus_gpu_addr         : out unsigned(3 downto 0); 
        bus_gpu_dataWrite    : out std_logic_vector(31 downto 0);
        bus_gpu_read         : out std_logic;
        bus_gpu_write        : out std_logic;
        bus_gpu_dataRead     : in  std_logic_vector(31 downto 0);
        bus_gpu_stall        : in  std_logic;

        bus_mdec_addr        : out unsigned(3 downto 0); 
        bus_mdec_dataWrite   : out std_logic_vector(31 downto 0);
        bus_mdec_read        : out std_logic;
        bus_mdec_write       : out std_logic;
        bus_mdec_dataRead    : in  std_logic_vector(31 downto 0);

        spu_memctrl          : in  unsigned(13 downto 0);
        bus_spu_addr         : out unsigned(9 downto 0) := (others => '0'); 
        bus_spu_dataWrite    : out std_logic_vector(15 downto 0);
        bus_spu_read         : out std_logic;
        bus_spu_write        : out std_logic;
        bus_spu_dataRead     : in  std_logic_vector(15 downto 0);

        ex2_memctrl          : in  unsigned(13 downto 0);
        bus_exp2_addr        : out unsigned(12 downto 0); 
        bus_exp2_dataWrite   : out std_logic_vector(7 downto 0);
        bus_exp2_read        : out std_logic;
        bus_exp2_write       : out std_logic;
        bus_exp2_dataRead    : in  std_logic_vector(7 downto 0);

        ex3_memctrl          : in  unsigned(13 downto 0);
        --bus_exp3_dataWrite   : out std_logic_vector(7 downto 0);
        bus_exp3_read        : out std_logic;
        --bus_exp3_write       : out std_logic;
        bus_exp3_dataRead    : in  std_logic_vector(15 downto 0);

        com0_delay           : in  unsigned(3 downto 0);
        com1_delay           : in  unsigned(3 downto 0);
        com2_delay           : in  unsigned(3 downto 0);
        com3_delay           : in  unsigned(3 downto 0);

        loading_savestate    : in  std_logic;
        SS_reset             : in  std_logic
    );
end entity;

architecture arch of cpu_mux is

    signal ram_cpu_be             : std_logic_vector(3 downto 0) := (others => '0');
    signal ram_cpu_Adr            : std_logic_vector(24 downto 0);
    signal ram_dma_Adr            : std_logic_vector(22 downto 0) := (others => '0');
    signal ram8mb                 : std_logic := '0';
    signal ram_cpu_rnw            : std_logic := '0';
    signal ram_cpu_cache          : std_logic := '0';
    signal ram_cpu_ena            : std_logic := '0';
    signal ram_cpu_done           : std_logic := '0';
    signal ram_next_cpu           : std_logic;
    signal mem_request         	  : std_logic;
    signal mem_rnw             	  : std_logic; 
    signal mem_isData          	  : std_logic; 
    signal mem_isCache         	  : std_logic;
    signal mem_oldtagvalids    	  : std_logic_vector(3 downto 0);      
    signal mem_addressInstr    	  : unsigned(31 downto 0); 
    signal mem_addressData     	  : unsigned(31 downto 0); 
    signal mem_reqsize         	  : unsigned(1 downto 0); 
    signal mem_writeMask       	  : std_logic_vector(3 downto 0); 
    signal mem_dataWrite       	  : std_logic_vector(31 downto 0); 
    signal mem_dataRead           : std_logic_vector(31 downto 0); 
    signal mem_done               : std_logic;
    signal mem_fifofull           : std_logic;
    signal mem_tagvalids          : std_logic_vector(3 downto 0);

    signal SS_DataWrite           : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_Adr                 : unsigned(18 downto 0) := (others => '0');
    signal SS_wren                : std_logic_vector(16 downto 0) := (others => '0');
    signal SS_rden                : std_logic_vector(16 downto 0) := (others => '0');
    signal SS_DataRead_CPU        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_GPU        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_GPUTiming  : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_DMA        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_GTE        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_JOYPAD     : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_MDEC       : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_MEMORY     : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_TIMER      : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_SOUND      : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_IRQ        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_SIO        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_SCP        : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_DataRead_CD         : std_logic_vector(31 downto 0) := (others => '0');
    signal SS_idle_cpu			  : std_logic := '0';

    signal dma_cache_Adr          : std_logic_vector(20 downto 0) := (others => '0');
    signal dma_cache_data         : std_logic_vector(31 downto 0) := (others => '0');
    signal dma_cache_write        : std_logic := '0';
    signal ram_dma_ena            : std_logic := '0';

    signal debug_firstGTE		  : std_logic := '0';

begin

    ram_Adr     <=  "00" & ram_dma_Adr(22 downto 0) when (cpuPaused = '1' and ram8mb = '1') else 
                    "0000" & ram_dma_Adr(20 downto 0) when (cpuPaused = '1' and ram8mb = '0') else 
                    ram_cpu_Adr(24 downto 23) &        ram_cpu_Adr(22 downto 0) when (ram8mb = '1') else
                    ram_cpu_Adr(24 downto 23) & "00" & ram_cpu_Adr(20 downto 0);
    ram_be      <=  ram_cpu_be;
    ram_rnw     <=  '1'             when (cpuPaused = '1') else ram_cpu_rnw;      
    ram_ena     <=  ram_dma_ena     when (cpuPaused = '1') else ram_cpu_ena;      
    -- ram_dma     <=  '1'             when (cpuPaused = '1') else '0';      
    ram_cache   <=  '0'             when (cpuPaused = '1') else ram_cpu_cache;   
    process (clk1x)
    begin
        if rising_edge(clk1x) then

            if (ram_ena = '1') then
                ram_next_cpu <= '0';
                if (cpuPaused = '0') then
                    ram_next_cpu <= '1';
                end if;
            end if;

        end if;
    end process;
   
   ram_cpu_done <= ram_done and ram_next_cpu;

imemorymux : entity work.memorymux
   port map
   (
      clk1x                => clk1x,
      clk2x                => clk2x,
      ce                   => ce,   
      reset                => reset_intern,
      
      pauseNext            => cpuPaused,
      isIdle               => memMuxIdle,
         
      loadExe              => loadExe,
      exe_initial_pc       => exe_initial_pc,  
      exe_initial_gp       => exe_initial_gp,  
      exe_load_address     => exe_load_address,
      exe_file_size        => exe_file_size,   
      exe_stackpointer     => exe_stackpointer,
      reset_exe            => reset_exe,
      
      fastboot             => fastboot,
      TURBO                => TURBO_MEM,
      region_in            => biosregion,
      PATCHSERIAL          => PATCHSERIAL,
            
      ram_dataWrite        => ram_dataWrite,
      ram_dataRead         => ram_dataRead32,  
      ram_Adr              => ram_cpu_Adr,  
      ram_be               => ram_cpu_be,        
      ram_rnw              => ram_cpu_rnw,      
      ram_ena              => ram_cpu_ena,   
      ram_cache            => ram_cpu_cache,      
      ram_done             => ram_cpu_done,
      
      mem_in_request       => mem_request,  
      mem_in_rnw           => mem_rnw,      
      mem_in_isData        => mem_isData,      
      mem_in_isCache       => mem_isCache,      
      mem_in_oldtagvalids  => mem_oldtagvalids,  
      mem_in_addressInstr  => mem_addressInstr,  
      mem_in_addressData   => mem_addressData,  
      mem_in_reqsize       => mem_reqsize,  
      mem_in_writeMask     => mem_writeMask,
      mem_in_dataWrite     => mem_dataWrite,
      mem_dataRead         => mem_dataRead, 
      mem_done             => mem_done,
      mem_fifofull         => mem_fifofull,  
      mem_tagvalids        => mem_tagvalids,

      bios_memctrl         => bios_memctrl,

      ex1_memctrl          => ex1_memctrl,
      --bus_exp1_addr        => bus_exp1_addr,   
      --bus_exp1_dataWrite   => bus_exp1_dataWrite,
      bus_exp1_read        => bus_exp1_read,   
      --bus_exp1_write       => bus_exp1_write,  
      bus_exp1_dataRead    => bus_exp1_dataRead,
      
      bus_memc_addr        => bus_memc_addr,     
      bus_memc_dataWrite   => bus_memc_dataWrite,
      bus_memc_read        => bus_memc_read,     
      bus_memc_write       => bus_memc_write,    
      bus_memc_dataRead    => bus_memc_dataRead,   
      
      bus_pad_addr         => bus_pad_addr,     
      bus_pad_dataWrite    => bus_pad_dataWrite,
      bus_pad_read         => bus_pad_read,     
      bus_pad_write        => bus_pad_write,    
      bus_pad_writeMask    => bus_pad_writeMask,
      bus_pad_dataRead     => bus_pad_dataRead,       
      
      bus_sio_addr         => bus_sio_addr,     
      bus_sio_dataWrite    => bus_sio_dataWrite,
      bus_sio_read         => bus_sio_read,     
      bus_sio_write        => bus_sio_write,    
      bus_sio_writeMask    => bus_sio_writeMask,
      bus_sio_dataRead     => bus_sio_dataRead, 

      bus_memc2_addr       => bus_memc2_addr,     
      bus_memc2_dataWrite  => bus_memc2_dataWrite,
      bus_memc2_read       => bus_memc2_read,     
      bus_memc2_write      => bus_memc2_write,    
      bus_memc2_dataRead   => bus_memc2_dataRead, 

      bus_irq_addr         => bus_irq_addr,     
      bus_irq_dataWrite    => bus_irq_dataWrite,
      bus_irq_read         => bus_irq_read,     
      bus_irq_write        => bus_irq_write,    
      bus_irq_dataRead     => bus_irq_dataRead,       
      
      bus_dma_addr         => bus_dma_addr,     
      bus_dma_dataWrite    => bus_dma_dataWrite,
      bus_dma_read         => bus_dma_read,     
      bus_dma_write        => bus_dma_write,    
      bus_dma_dataRead     => bus_dma_dataRead,     

      bus_tmr_addr         => bus_tmr_addr,     
      bus_tmr_dataWrite    => bus_tmr_dataWrite,
      bus_tmr_read         => bus_tmr_read,     
      bus_tmr_write        => bus_tmr_write,    
      bus_tmr_dataRead     => bus_tmr_dataRead,  

      cd_memctrl           => cd_memctrl,
      bus_cd_addr          => bus_cd_addr,     
      bus_cd_dataWrite     => bus_cd_dataWrite,
      bus_cd_read          => bus_cd_read,     
      bus_cd_write         => bus_cd_write,    
      bus_cd_dataRead      => bus_cd_dataRead,      
      
      bus_gpu_addr         => bus_gpu_addr,     
      bus_gpu_dataWrite    => bus_gpu_dataWrite,
      bus_gpu_read         => bus_gpu_read,     
      bus_gpu_write        => bus_gpu_write,    
      bus_gpu_dataRead     => bus_gpu_dataRead,
      bus_gpu_stall        => bus_gpu_stall,
      
      bus_mdec_addr        => bus_mdec_addr,     
      bus_mdec_dataWrite   => bus_mdec_dataWrite,
      bus_mdec_read        => bus_mdec_read,     
      bus_mdec_write       => bus_mdec_write,    
      bus_mdec_dataRead    => bus_mdec_dataRead, 
      
      spu_memctrl          => spu_memctrl, 
      bus_spu_addr         => bus_spu_addr,     
      bus_spu_dataWrite    => bus_spu_dataWrite,
      bus_spu_read         => bus_spu_read,     
      bus_spu_write        => bus_spu_write,    
      bus_spu_dataRead     => bus_spu_dataRead, 
      
      ex2_memctrl          => ex2_memctrl,
      bus_exp2_addr        => bus_exp2_addr,     
      bus_exp2_dataWrite   => bus_exp2_dataWrite,
      bus_exp2_read        => bus_exp2_read,     
      bus_exp2_write       => bus_exp2_write,    
      bus_exp2_dataRead    => bus_exp2_dataRead,
      
      ex3_memctrl          => ex3_memctrl,
      --bus_exp3_dataWrite   => bus_exp3_dataWrite,
      bus_exp3_read        => bus_exp3_read,     
      --bus_exp3_write       => bus_exp3_write,    
      bus_exp3_dataRead    => bus_exp3_dataRead, 
      
      com0_delay           => com0_delay,
      com1_delay           => com1_delay,
      com2_delay           => com2_delay,
      com3_delay           => com3_delay,
      
      loading_savestate    => loading_savestate,
      SS_reset             => SS_reset,
      SS_DataWrite         => SS_DataWrite,
      SS_Adr               => SS_Adr(18 downto 0),
      SS_wren_SDRam        => SS_wren(16),
      SS_rden_SDRam        => SS_rden(16)
   );

   icpu : entity work.cpu
   port map
   (
      clk1x             => clk1x,
      clk2x             => clk2x,
      clk3x             => clk3x,
      ce                => ce,   
      reset             => reset_intern,
      
      TURBO             => TURBO_COMP,
      TURBO_CACHE       => TURBO_CACHE,
      TURBO_CACHE50     => TURBO_CACHE50,
         
      irqRequest        => '0',
      dmaStallCPU       => '0',
      cpuPaused         => cpuPaused,
      
    --   error             => errorCPU,
    --   error2            => errorCPU2,
         
      mem_request       => mem_request,  
      mem_rnw           => mem_rnw,      
      mem_isData        => mem_isData,      
      mem_isCache       => mem_isCache, 
      mem_oldtagvalids  => mem_oldtagvalids,      
      mem_addressInstr  => mem_addressInstr,  
      mem_addressData   => mem_addressData,  
      mem_reqsize       => mem_reqsize,  
      mem_writeMask     => mem_writeMask,
      mem_dataWrite     => mem_dataWrite,
      mem_dataRead      => mem_dataRead, 
      mem_done          => mem_done,
      mem_fifofull      => mem_fifofull,
      mem_tagvalids     => mem_tagvalids,
      
      cache_wr          => cache_wr,  
      cache_data        => cache_data,
      cache_addr        => cache_addr,
      
    --   stallNext         => stallNext, -- output
      
      dma_cache_Adr     => dma_cache_Adr,  
      dma_cache_data    => dma_cache_data, 
      dma_cache_write   => dma_cache_write,  
      
      ram_dataRead      => ram_dataRead32,    
      ram_rnw           => ram_cpu_rnw,
      ram_done          => ram_cpu_done,
      
      gte_busy          => gte_busy, 
      gte_readEna       => gte_readEna,
      gte_readAddr      => gte_readAddr, 
      gte_readData      => gte_readData, 
      gte_writeAddr     => gte_writeAddr,
      gte_writeData     => gte_writeData,
      gte_writeEna      => gte_writeEna, 
      gte_cmdData       => gte_cmdData,  
      gte_cmdEna        => gte_cmdEna, 

      SS_reset          => SS_reset,
      SS_DataWrite      => SS_DataWrite,
      SS_Adr            => SS_Adr(7 downto 0),   
      SS_wren_CPU       => SS_wren(0),     
      SS_wren_SCP       => SS_wren(12),  
      SS_rden_CPU       => SS_rden(0),     
      SS_rden_SCP       => SS_rden(12),        
      SS_DataRead_CPU   => SS_DataRead_CPU,
      SS_DataRead_SCP   => SS_DataRead_SCP,
      SS_idle           => SS_idle_cpu,
      
-- synthesis translate_off
    --   cpu_done          => cpu_done,  
    --   cpu_export        => cpu_export,
-- synthesis translate_on
      
      debug_firstGTE    => debug_firstGTE
   );

end architecture;