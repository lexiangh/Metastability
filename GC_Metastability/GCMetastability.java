import java.util.Random;
import java.lang.Math;
import java.lang.Thread;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.lang.management.ManagementFactory;
import java.lang.management.RuntimeMXBean;
import java.io.FileWriter;
import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

class Result{
    public long arrival_t;
    public long start_t;
    public long completion_t;
    public long arrival_uptime;
    public long completion_uptime;
}

class Global{
    public static int MAX_T = 100;
    public static String record_filepath="./exp_record.csv";

    public static int num_reqs;
    public static Result[] results;

    public static boolean warmup = true;
    public static int warmup_endtime_offset=20; //in second
    public static int warmup_sleep_dur=10000; //in ms, happens after warmup
    public static double warmup_interarrival_time = 0.01; // in s
    public static int num_warmup_reqs = (int)((1/warmup_interarrival_time) * warmup_endtime_offset);
    public static int curr_arrival_rate;

    // load-spike trigger specific configs
    public static int stage_dur;
    public static int original_arrival_rate;
    public static int highest_arrival_rate; 
    public static int arr_after_first_load_shedding;
    public static int arr_after_second_load_shedding;
    public static int arr_after_thrid_load_shedding;
    
    // capacity degradation trigger specific configs
    public static int trigger_dur;
    public static int trigger_offset; // determine when to add a trigger
    public static boolean apply_trigger = false;
    
    public static boolean auto_detect = false; // detect whether the current experiment shows a metastable failure or not
    public static int num_data_before_trigger=0;
    public static long sum_latency_before_trigger=0;
    public static int num_reqs_back_to_normal_latency = 0;
    public static int window_for_success = 30; //30sec samples after trigger back to normal is a success
}

class Task implements Runnable{
    private RuntimeMXBean bean = ManagementFactory.getRuntimeMXBean();
    private int i;
    
    public Task(int index){
	i = index;
    }
        
    public void run()
    {
	try{
	    //Each thread is 0.5MB
	    Global.results[i].start_t = System.nanoTime();
	    int[][] intArray = new int[256*256][];
	    
	    for (int i = 0; i < 256*256; i++){
		intArray[i] = new int[2];
		for (int j = 0; j < 2; j++){
		    intArray[i][j] = i;
		}
	    }
	    Thread.sleep(100); //sleep 0.1s
	    int local_elem = intArray[0][0];
	    Global.results[i].completion_t = System.nanoTime();
	    Global.results[i].completion_uptime = bean.getUptime();

	    // recording latency info for detecting metastable failures
	    if (Global.apply_trigger && i > Global.num_warmup_reqs && i < Global.num_warmup_reqs + Global.curr_arrival_rate * Global.trigger_offset){
                Global.num_data_before_trigger += 1;
                Global.sum_latency_before_trigger += Global.results[i].completion_t - Global.results[i].arrival_t;
            } else if (Global.apply_trigger && Global.auto_detect && i > Global.num_warmup_reqs + Global.curr_arrival_rate * (Global.trigger_offset + Global.trigger_dur/1e3 + 10)) {
		// start detecting after 10s for system to stabalize
		double avg_latency_before_trigger = Global.sum_latency_before_trigger/Global.num_data_before_trigger;
                long curr_latency = Global.results[i].completion_t-Global.results[i].arrival_t;

                if ((double)curr_latency < 1.1*avg_latency_before_trigger){
                    Global.num_reqs_back_to_normal_latency += 1;
                }
		
		if(Global.num_reqs_back_to_normal_latency > Global.window_for_success * Global.curr_arrival_rate){
                    System.out.println("System succeeds due to latency(ms): " + curr_latency/1e6 + " is below or about the same as the average before the trigger: " + avg_latency_before_trigger/1e6);
                    FileWriter fw = new FileWriter(Global.record_filepath, true);
                    fw.write(Global.curr_arrival_rate + "," + Global.trigger_dur + "," + Global.num_reqs/Global.curr_arrival_rate + "," + "Success\n");
                    fw.close();
                    System.exit(0);
                }
	    }
	}
	catch (Exception e){
	    System.out.println("Exception is caught");
	    e.printStackTrace(System.out);
	    System.exit(0);
	}
    }
}

public class GCMetastability{
    static Random rand = new Random();
    
    //given arrival rate lambda, generate waiting time in exponetial distribution
    public static double getExp(double lambda){
	return Math.log(1-rand.nextDouble())/(-lambda);
    }

    public static void main(String[] args){
	if (args.length < 4){
	    System.out.println("Please enter arrival rate, trigger duration(ms), experiments duration(s) and metastable failure detection enabled");
	    System.exit(0);
	}
	
	Global.curr_arrival_rate = Integer.parseInt(args[0]);
	Global.trigger_dur = Integer.parseInt(args[1]);

	if (Integer.parseInt(args[3]) > 0) {
	    Global.auto_detect = true;
	}
	
	if (Global.trigger_dur < 0) { // load-spike trigger
	    // setting up arrival rate pattern
	    int rps_level_interval = 50;
	    Global.original_arrival_rate = Global.curr_arrival_rate;
	    Global.highest_arrival_rate = Global.original_arrival_rate + 2 * rps_level_interval;
	    Global.arr_after_first_load_shedding = Global.highest_arrival_rate - rps_level_interval;
	    Global.arr_after_second_load_shedding = Global.arr_after_first_load_shedding - rps_level_interval;
	    Global.arr_after_thrid_load_shedding = Global.arr_after_second_load_shedding - rps_level_interval;

	    // setting up experiment durations
	    Global.stage_dur = (int)(Integer.parseInt(args[2]) / 5); // 5 stages of diffferent load levels
	    Global.num_reqs = Global.num_warmup_reqs + (Global.original_arrival_rate * Global.stage_dur) + (Global.highest_arrival_rate * Global.stage_dur) + (Global.arr_after_first_load_shedding * Global.stage_dur) + (Global.arr_after_second_load_shedding * Global.stage_dur) + (Global.arr_after_thrid_load_shedding * Global.stage_dur);
	    System.out.println("Running experiment with load-spike trigger");
	} else {// capacity degradation trigger
	    if (Global.trigger_dur >= 0) {
		Global.apply_trigger = true;
	    }
	    Global.num_reqs = Global.curr_arrival_rate * Integer.parseInt(args[2]);
	    Global.trigger_offset = Global.warmup_endtime_offset + (int)(Global.warmup_sleep_dur/1000); // apply trigger right after warmup
	    System.out.println("Running experiment with capacity degradation trigger [rps_triggerDur(ms)_expDur(s)]: " + Global.curr_arrival_rate + "_" + Global.trigger_dur + "_" + Global.num_reqs/Global.curr_arrival_rate);
	}
	
	//add time padding for jvm initialization
	try{
	    Thread.sleep(2000); 
	}catch (Exception e){
	    System.out.println(e);
	    System.exit(0);
	}
	
	ExecutorService pool = Executors.newFixedThreadPool(Global.MAX_T);
	RuntimeMXBean bean = ManagementFactory.getRuntimeMXBean();

	String filepath = "job.csv";

	Global.results = new Result[Global.num_reqs];
	for(int i=0; i<Global.num_reqs; i++){
	    Global.results[i] = new Result();
	}
	    	
	long start_time = System.nanoTime();
	long measurement_start_time = System.nanoTime();
	long arrival_time = start_time;

	if (!Global.warmup) {
	    Global.num_warmup_reqs = 0;
	}

	for (int i=0; i<Global.num_reqs; i++){
	    try{
		double sleep_dur = 0;
		if (i < Global.num_warmup_reqs){
		    sleep_dur = Global.warmup_interarrival_time;
		}
		else{
		    sleep_dur = getExp(Global.curr_arrival_rate);
		}
		arrival_time += sleep_dur * 1e9;
		
		long current_time = System.nanoTime();
		if (arrival_time > current_time){
		    Thread.sleep((long)((arrival_time - current_time)/1e6));
		}
		
		Global.results[i].arrival_t = arrival_time;
		Global.results[i].arrival_uptime = bean.getUptime();
		Runnable r = new Task(i);
		pool.execute(r);
		
		if (Global.warmup && (i == Global.num_warmup_reqs)){
		    // For warmup
		    System.out.println("Warm-up finished, sleeping...");
		    Thread.sleep(Global.warmup_sleep_dur);
		    arrival_time += Global.warmup_sleep_dur * 1e6;
		    //Global.curr_arrival_rate = Global.original_arrival_rate;
		    System.out.println("Start running experiment at RPS=" + Global.curr_arrival_rate);
		    measurement_start_time = System.nanoTime();
		} else if (Global.apply_trigger && i == Global.num_warmup_reqs + (Global.curr_arrival_rate * Global.trigger_offset)) {
		    // For applying capacity degradation trigger
		    System.out.println("Applying capacity degradation trigger...");
                    Thread.sleep(Global.trigger_dur);
                    System.out.println("Finished applying capacity degradation trigger.");
		}
		
		if (Global.trigger_dur < 0) { //load-spike trigger
		    if (i == Global.num_warmup_reqs + (Global.original_arrival_rate * Global.stage_dur)){
			System.out.println("Goes up to highest RPS level...");
			Global.curr_arrival_rate = Global.highest_arrival_rate;
		    }
		    else if (i == Global.num_warmup_reqs + (Global.original_arrival_rate * Global.stage_dur) + (Global.highest_arrival_rate * Global.stage_dur)){
			System.out.println("1st load shedding...");
			Global.curr_arrival_rate = Global.arr_after_first_load_shedding;
		    }
		    else if (i == Global.num_warmup_reqs + (Global.original_arrival_rate * Global.stage_dur) + (Global.highest_arrival_rate * Global.stage_dur) + (Global.arr_after_first_load_shedding * Global.stage_dur)){
			System.out.println("2nd load shedding...");
			Global.curr_arrival_rate = Global.arr_after_second_load_shedding;
		    }
		    else if (i == Global.num_warmup_reqs + (Global.original_arrival_rate * Global.stage_dur) + (Global.highest_arrival_rate * Global.stage_dur) + (Global.arr_after_first_load_shedding * Global.stage_dur) + (Global.arr_after_second_load_shedding * Global.stage_dur)){
			System.out.println("3rd load shedding...");
			Global.curr_arrival_rate = Global.arr_after_thrid_load_shedding;
		    }
		}
		
	    } catch (Exception e){
		System.out.println("Exception is caught");
		e.printStackTrace(System.out);
		System.exit(0);
	    } catch (OutOfMemoryError E){
		System.exit(0);
	    }
	}
	pool.shutdown();

	try{
	    pool.awaitTermination(60, TimeUnit.SECONDS);
	} catch (InterruptedException ex) {
	    pool.shutdownNow();
	    Thread.currentThread().interrupt();
	}

	long completion_time = System.nanoTime();
	double throughput = (double)(Global.num_reqs - Global.num_warmup_reqs)/((double)(completion_time-measurement_start_time)/1e9);
	System.out.println("Throughput is: " + throughput);
	
	if(Global.apply_trigger){
            double avg_latency_before_trigger = Global.sum_latency_before_trigger/Global.num_data_before_trigger;
            System.out.println("Average latency before trigger is: " + avg_latency_before_trigger/1e6 + "ms from " + Global.num_data_before_trigger + " samples.");
        }

	//write to csv: arrival_time, start_time, completion_time, completion_uptimeime (using bean)
	try{
	    FileWriter fw = new FileWriter(filepath, true);
	    fw.write("arrival_t," + "start_t," + "completion_t," + "arrival_uptime," +"completion_uptime\n");
	    for(int i = 0; i < Global.num_reqs; i++){
		fw.write(Global.results[i].arrival_t + "," + Global.results[i].start_t + "," + Global.results[i].completion_t + "," + Global.results[i].arrival_uptime + "," + Global.results[i].completion_uptime + "\n");
	    }
	    fw.close();
	    
	    if (Global.auto_detect){
		FileWriter fw2 = new FileWriter(Global.record_filepath, true);
		fw2.write(Global.curr_arrival_rate + "," + Global.trigger_dur + "," + Global.num_reqs/Global.curr_arrival_rate + ",Failure\n");
		fw2.close();
		System.out.println("System showed metastable failure due to high latency persists till the end of the experiment.");
	    }
	} catch (IOException ioe){
	    System.out.println(ioe);
	    ioe.printStackTrace(System.out);
	    System.exit(0);
	}
    }
}

