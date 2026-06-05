package service

import (
	"fmt"
	http "net/http"
)

type UserService struct{}

func NewUserService() *UserService {
	return &UserService{}
}

func (s *UserService) Load(name string) string {
	fmt.Println(name)
	http.Get("/user")
	return normalize(name)
}

func normalize(value string) string {
	return value
}
