testfile = """package main

import "fmt"

type game struct {
	duration int
	distance int
}

// // part 1 test
// var games = []game{
// 	{7, 9},
// 	{15, 40},
// 	{30, 200},
// }

// // part 1 actual
// var games = []game{
// 	{45, 305},
// 	{97, 1062},
// 	{72, 1110},
// 	{95, 1695},
// }

// // part 2 test
// var games = []game{{71530, 940200}}

// part 2 actual
var games = []game{{45977295, 305106211101695}}

func main() {
	result := 1
	for _, g := range games {
		// distance = velocity * time = h*(t - h), where h is hold time and t is race duration
		// solve for:
		//     h*(t - h) > distance
		winningStrategies := 0
		for h := 1; h < g.duration; h++ {
			if h*(g.duration-h) > g.distance {
				winningStrategies++
			}
		}

		fmt.Println("winning strategies:", winningStrategies)
		result *= winningStrategies
	}

	fmt.Println(result)
}
"""
