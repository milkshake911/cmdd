function recursiveTimerA() {
	if (document.getElementById('limitType').checked) {
		document.getElementById('TimerA').style.display = 'block';
	}
	else if (document.getElementById('marketType').checked) {
		document.getElementById('TimerA').style.display = 'none';
	}

}

function recursiveTimerB(){
	if (document.getElementById('limitTypeB').checked) {
		document.getElementById('TimerB').style.display = 'block';
	}
	else if (document.getElementById('marketTypeB').checked) {
		document.getElementById('TimerB').style.display = 'none';
	}
}


function optionsTrade(selectOptions) {
	index = selectOptions.selectedIndex
	if (index == 1) {
		document.getElementById('timerOptions').style.display = 'block';
		document.getElementById('percentageOptions').style.display = 'none';
	}
	else {
		document.getElementById('timerOptions').style.display = 'none';
		document.getElementById('percentageOptions').style.display = 'block';
	}

}

function disableParamaterA(checkBox){
	if (checkBox.checked){
		document.getElementById('container-inputs-a').disabled = true;
		document.getElementById('container-inputs-a').style.opacity = "0.6";
	}else{
		document.getElementById('container-inputs-a').disabled = false;
		document.getElementById('container-inputs-a').style.opacity = "1";
	}
}

function disableParamaterB(checkBox){
	if (checkBox.checked){
		document.getElementById('container-inputs-b').disabled = true;
		document.getElementById('container-inputs-b').style.opacity = "0.6";
	}else{
		document.getElementById('container-inputs-b').disabled = false;
		document.getElementById('container-inputs-b').style.opacity = "1";
	}
}

function disableQty(checkBox) {
	if (checkBox.checked){
		document.getElementById('quantity').disabled = true;
		document.getElementById('quantity').style.opacity = "0.6";
	}
	else {
		document.getElementById('quantity').disabled = false;
		document.getElementById('quantity').style.opacity = "1";
	}
}

function disablePipsBuy(checkBox) {
	if (checkBox.checked) {
		document.getElementById('pips_buy').disabled = true;
		document.getElementById('pips_buy').style.opacity = "0.6";
	}
	else {
		document.getElementById('pips_buy').disabled = false;
		document.getElementById('pips_buy').style.opacity = "1";
	}
}


function disablePipsSell(checkBox) {
	if (checkBox.checked) {
		document.getElementById('pips_sell').disabled = true;
		document.getElementById('pips_sell').style.opacity = "0.6";
	}
	else {
		document.getElementById('pips_sell').disabled = false;
		document.getElementById('pips_sell').style.opacity = "1";
	}
}


function disableMaxPosBuy(checkBox) {
	if (checkBox.checked) {
		document.getElementById('max_pos_buy').disabled = true;
		document.getElementById('max_pos_buy').style.opacity = "0.6";
	}
	else {
		document.getElementById('max_pos_buy').disabled = false;
		document.getElementById('max_pos_buy').style.opacity = "1";
	}
}

function disableMaxPosSell(checkBox) {
	if (checkBox.checked) {
		document.getElementById('max_pos_sell').disabled = true;
		document.getElementById('max_pos_sell').style.opacity = "0.6";
	}
	else {
		document.getElementById('max_pos_sell').disabled = false;
		document.getElementById('max_pos_sell').style.opacity = "1";
	}
}

function disableCapital(checkBox) {
	if (checkBox.checked) {
		document.getElementById('capital_fund').disabled = true;
		document.getElementById('capital_fund').style.opacity = "0.6";
	}
	else {
		document.getElementById('capital_fund').disabled = false;
		document.getElementById('capital_fund').style.opacity = "1";
	}
}


function marketOrder(checkBox){
	if(checkBox.checked){
		document.getElementById('limit_price').disabled = true;
		document.getElementById('limit_price').style.opacity = "0.6";
	}
	else{
		document.getElementById('limit_price').disabled = false;
		document.getElementById('limit_price').style.opacity = "1";
	}
}