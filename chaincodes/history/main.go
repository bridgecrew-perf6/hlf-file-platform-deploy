package main

import (
	"encoding/json"

	"github.com/hyperledger/fabric-chaincode-go/shim"
	"github.com/hyperledger/fabric-protos-go/peer"
)

type CC struct {
}

type HDFSHistoryValue []struct {
	Type      string `json:"type"`
	Timestamp string `json:"timestamp"`
	Detail    string `json:"detail"`
}

func (c *CC) Init(stub shim.ChaincodeStubInterface) peer.Response {
	return shim.Success([]byte("OK"))
}

func (c *CC) Invoke(stub shim.ChaincodeStubInterface) peer.Response {
	var f, args = stub.GetFunctionAndParameters()
	switch f {
	case "init":
		return c.Init(stub)

	case "addHistory":
		key := args[0]
		valueJson, err := stub.GetState(key)

		var value HDFSHistoryValue
		var appendValue HDFSHistoryValue

		json.Unmarshal(valueJson, &value)
		json.Unmarshal([]byte(args[1]), &appendValue)

		for i := 0; i < len(appendValue); i++ {
			value = append(value, appendValue[i])
		}

		valueJson, err = json.Marshal(value)

		if err = stub.PutState(key, valueJson); err != nil {
			return shim.Error(err.Error())
		}
		return shim.Success([]byte("History Update Success. Key : " + key))

	case "queryHistory":
		key := args[0] + "|" + args[1]

		value, err := stub.GetState(key)
		if err != nil {
			return shim.Error(err.Error())
		}
		return shim.Success([]byte(value))
	}
	return shim.Error("No function is supported for " + f)
}

func main() {
	err := shim.Start(new(CC))
	if err != nil {
		panic(err.Error())
	}
}
