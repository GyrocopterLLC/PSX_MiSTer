#include <cstdio>
#include <iostream>
#include <cstdlib>
#include <climits>
#include <cstring>
#include <vector>
#include <cctype>

#include "Vcpu.h"
#include "verilated.h"
//#include <verilated_vcd_c.h>
#include <verilated_fst_c.h>

#define TRACE_ON

using namespace std;

bool trace = false;
// Default 10 million clock cycles
long long max_sim_time = 10000000LL;
long long start_trace_time = 0;

void usage() {
	printf("Usage: sim [-t] [-c T]\n");
	printf("  -t     output trace file waveform.vcd\n");
	printf("  -s T0  start tracing from time T0\n");
	printf("  -c T   limit simulate lenght to T time steps. T=0 means infinite.\n");
}

VerilatedFstC *m_trace;
Vcpu* top = new Vcpu;

// split by spaces
vector<string> tokenize(string s);
long long parse_num(string s);
void trace_on();
void trace_off();

vluint64_t sim_time;
int main(int argc, char** argv, char** env) {
	Verilated::commandArgs(argc, argv);

	// parse options
	for (int i = 1; i < argc; i++) {
		char *eptr;
		if (strcmp(argv[i], "-t") == 0) {
			trace = true;
			printf("Tracing ON\n");
		} else if (strcmp(argv[i], "-c") == 0 && i+1 < argc) {
			max_sim_time = strtoll(argv[++i], &eptr, 10); 
			if (max_sim_time == 0)
				printf("Simulating forever.\n");
			else
				printf("Simulating %lld steps\n", max_sim_time);
		} else if (strcmp(argv[i], "-s") == 0 && i+1 < argc) {
			start_trace_time = strtoll(argv[++i], &eptr, 10);
			printf("Start tracing from %lld\n", start_trace_time);
		} else {
			printf("Unrecognized option: %s\n", argv[i]);
			usage();
			exit(1);
		}
	}

	//VerilatedVcdC *m_trace;
	if (trace)
		trace_on();

	bool done = false;

	while (!done) {

		while (max_sim_time == 0 || sim_time < max_sim_time) {
			if(sim_time < 100) {
				top->SS_reset = 1;
				top->reset = 1;
			} else {
				top->SS_reset = 0;
				top->reset = 0;
			}

			// time = 0, all clocks change
			top->clk3x ^= 1;
			top->clk2x ^= 1;
			top->clk1x ^= 1;
			top->eval();
			if (trace && sim_time >= start_trace_time)
				m_trace->dump(sim_time);
			sim_time += 2;
			// time = 2, clk3x change
			top->clk3x ^= 1;
			top->eval();
			if (trace && sim_time >= start_trace_time)
				m_trace->dump(sim_time);
			sim_time++;
			// time = 3, clk2x change
			top->clk2x ^= 1;
			top->eval();
			if (trace && sim_time >= start_trace_time)
				m_trace->dump(sim_time);
			sim_time++;
			// time = 4, clk3x change
			top->clk3x ^= 1;
			top->eval();
			if (trace && sim_time >= start_trace_time)
				m_trace->dump(sim_time);
			sim_time += 2;
			// time = 6, all clocks change (back to beginning of loop)



		}

		printf("Simulation done, time=%lu\n", sim_time);
		printf("Choose: (S)imulate, (E)nd, (T)race On, or (O)ff\n");
		printf("  s 100m - simulate 100 million clock cycles\n");
		printf("  s 0    - simulate forever\n");
		printf("  s      - simulate 10 million clock cycles\n");
		do {
			string line;
			std::getline(cin, line);
			vector<string> ss = tokenize(line);
			if (ss.size() == 0) continue;
		    transform(ss[0].begin(), ss[0].end(), ss[0].begin(), ::tolower); 
			if (ss[0] == "s" || ss[0] == "simulate") {
				long long cycles = 10000000LL;
				if (ss.size() > 1) {
					cycles = parse_num(ss[1]);
					if (cycles == -1) {
						cout << "Cannot parse number: " << ss[1] << endl;
						continue;
					}
				}
				max_sim_time += cycles;
				break;
			} else if (ss[0] == "e" || ss[0] == "end") {
				done = true;
				break;
			} else if (ss[0] == "t" || ss[0] == "trace") {
				cout << "trace on" << endl;
				trace_on();
			} else if (ss[0] == "o" || ss[0] == "off") {
				cout << "trace off" << endl;
				trace_off();
			}
		} while (1);
	}

	if (m_trace)
		m_trace->close();
	delete top;

	return 0;
}

bool is_space(char c) {
	return c == ' ' || c == '\t';
}

vector<string> tokenize(string s) {
	string w;
	vector<string> r;

	for (int i = 0; i < s.size(); i++) {
		char c = s[i];
		if (is_space(c) && w.size() > 0) {
			r.push_back(w);
			w = "";
		}
		if (!is_space(c))
			w += c;
	}
	if (w.size() > 0)
		r.push_back(w);
	return r;
}

// parse something like 100m or 10k
// return -1 if there's an error
long long parse_num(string s) {
	long long times = 1;
	if (s.size() == 0)
		return -1;
	char last = tolower(s[s.size()-1]);
	if (last >= 'a' && last <= 'z') {
		s = s.substr(0, s.size()-1);
		if (last == 'k')
		 	times = 1000LL;
		else if (last == 'm')
			times = 1000000LL;
		else if (last == 'g')
			times = 1000000000LL;
		else 
			return -1;
	}
	return atoll(s.c_str()) * times;
}

void trace_on() {
	if (!m_trace) {
		//m_trace = new VerilatedVcdC;
		//m_trace->open("waveform.vcd");
		m_trace = new VerilatedFstC;
		top->trace(m_trace, 5);
		Verilated::traceEverOn(true);
		m_trace->open("waveform.fst");
	}
}

void trace_off() {
	if (m_trace) {
		top->trace(m_trace, 0);
	}
}
