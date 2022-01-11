/**
 * Author: Karl Pery
 * Filename: LiveChart.js
 * Purpose: Create a chart with Websocket API of Bybit
 * */

/*const crypto = require('crypto');

   var api_key = '{{ apiKey }}';
   var secret = '{{ apiSecret }}';
   var timestamp = Date.now() + 1000;
   var params = {
	   "order_id": "876b0ac1-bafe-4110-b404-6a7c8211a6d9",
	   "symbol": "BTCUSD",
	   "timestamp": timestamp,
	   "api_key": api_key,
   };

   console.log(getSignature(params, secret));

   function getSignature(paramaters, secret) {
	   var orderedParams = "";
	   Object.keys(paramaters  ).sort().forEach(function (key) {
		   orderedParams += key + "=" + paramaters[key] + "&";

	   });
	   orderedParams = orderedParams.substring(0, orderedParams.length - 1);
	   return crypto.createHmac('sha256', secret).update(orderedParams).digest('hex');
   }

   var bybitSocket = new WebSocket("wss://stream.bybit.com/realtime");
   bybitSocket.send('{"op":"auth","args":["{api_key}","{expires}","{signature}"]}')

   //bybitSocket.send('{"op":"subscribe","args":["klineV2.1.BTCUSD"]}')

   bybitSocket.on = function (event) {
	   console.log(event.data)
   };*/

