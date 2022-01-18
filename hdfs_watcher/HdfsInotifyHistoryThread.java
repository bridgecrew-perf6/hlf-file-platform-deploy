/*
Code reference :
HDFS Inotify : https://github.com/onefoursix/hdfs-inotify-example/blob/master/src/main/java/com/onefoursix/HdfsINotifyExample.java
HDFS Read : https://github.com/nsquare-jdzone/hadoop-examples/blob/master/ReadWriteHDFSExample/src/main/java/com/javadeveloperzone/ReadWriteHDFSExample.java
*/

import java.io.IOException;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.text.SimpleDateFormat;
import java.net.URI;
import java.net.URL;

import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import org.apache.commons.io.IOUtils;

import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import org.apache.hadoop.conf.Configuration;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import org.apache.hadoop.hdfs.DFSInotifyEventInputStream;
import org.apache.hadoop.hdfs.client.HdfsAdmin;
import org.apache.hadoop.hdfs.inotify.Event;
import org.apache.hadoop.hdfs.inotify.Event.CreateEvent;
import org.apache.hadoop.hdfs.inotify.Event.CreateEvent.INodeType;
import org.apache.hadoop.hdfs.inotify.Event.UnlinkEvent;
import org.apache.hadoop.hdfs.inotify.EventBatch;
import org.apache.hadoop.hdfs.inotify.MissingEventsException;

public class HdfsInotifyHistoryThread implements Runnable{

	DFSInotifyEventInputStream eventStream;

	HashMap<String, List<String>> map = new HashMap<>();

	public HdfsInotifyHistoryThread(DFSInotifyEventInputStream eventStream){
		this.eventStream = eventStream;
	}

	public String eventToStr(String key, List<String> values) {
		String str = String.format("{\"key\": \"%s\", \"value\": %s}", key, values);
		return str;
	}
	
	public String valueToStr(String type, long ts, String detail) {
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		Date date = new Date(ts);
		String timestamp = dateFormat.format(date);
		return String.format("{\"type\": \"%s\", \"timestamp\": \"%s\", \"detail\": \"%s\"}", type, timestamp, detail);
	}

	public void addMap(String user, String path, String value) throws IOException, ParseException {
		List<String> newVal;
		String key = String.format("%s|%s", user, path);
		if (map.containsKey(key)) {
			newVal = map.get(key);
		} else {
			newVal = new ArrayList<String>();
		}
		newVal.add(value);
		map.put(key, newVal);
	}

	public void addEvent(Event event) throws IOException, ParseException {
		switch (event.getEventType()) {
		case CREATE:
			CreateEvent createEvent = (CreateEvent) event;
			if (createEvent.getiNodeType() == INodeType.FILE) {
				addMap(
					createEvent.getOwnerName(),
					createEvent.getPath(),
					valueToStr("CREATE", createEvent.getCtime(), createEvent.toString()));
			}
			break;
		case UNLINK:
			UnlinkEvent unlinkEvent = (UnlinkEvent) event;
			addMap(
				"jjlee",
				unlinkEvent.getPath(),
				valueToStr("DELETE", unlinkEvent.getTimestamp(), unlinkEvent.toString()));
			break;
		default:
			break;
		}
	}

	@Override
	public void run() {
		int num_batch = 0;
		while(true){
			try {
				EventBatch batch = this.eventStream.poll();
				
				if (batch == null) {
					continue;
				}

				int num_events = 0;
				while (batch != null) {
					for (Event event : batch.getEvents()) {
						addEvent(event);
						num_events++;
					}
					System.out.println("[BATCH | EVENT NUMBER] " + num_batch + " | " +num_events);
					if (num_events >= 300) {
						break;
					}
					batch = this.eventStream.poll();
				}
				
				num_batch++;
				
				// Iterate map and make jsonarray of events
				List<String> events = new ArrayList<String>();
				for(String key : map.keySet()) {
					events.add(eventToStr(key, map.get(key)));
				}
				
				HttpRequestThread hrt = new HttpRequestThread(String.format("%s", events));
				Thread t = new Thread(hrt, "request");
				t.start();
				
				map.clear();
				Thread.sleep(1000);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	public static void main(String[] args) throws IOException, InterruptedException, MissingEventsException {

		URI uri = URI.create("hdfs://sun01:10001");
		Configuration conf = new Configuration();
		HdfsAdmin admin = new HdfsAdmin(uri, conf);

		DFSInotifyEventInputStream eventStream = admin.getInotifyEventStream();

		HdfsInotifyHistoryThread hih = new HdfsInotifyHistoryThread(eventStream);
		Thread t = new Thread(hih, "test");
		t.start();
	}
}

class HttpRequestThread implements Runnable {
    String arg;

    public HttpRequestThread(String arg) {
        this.arg = arg;
    }

	@Override
	public void run() {
		try {
			String result = "";
			HttpPost post = new HttpPost("http://127.0.0.1:8000/invoke/");

			post.setHeader("Cookie", "csrftoken=ZdBAo8hkhunGcxsfXI3AcOju3NelyvtxVHEn2gncukUJ1FmyCXwAXlAzjDGGYJhg");
			post.setHeader("X-CSRFToken", "ZdBAo8hkhunGcxsfXI3AcOju3NelyvtxVHEn2gncukUJ1FmyCXwAXlAzjDGGYJhg");
			post.setEntity(new StringEntity(this.arg));

			try (CloseableHttpClient httpClient = HttpClients.createDefault();
				CloseableHttpResponse response = httpClient.execute(post)) {

				result = EntityUtils.toString(response.getEntity());
			}
			// System.out.println("[WATCHER RESULT] "+result);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}