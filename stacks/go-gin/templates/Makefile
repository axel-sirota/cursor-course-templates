.PHONY: build run test lint migrate-up migrate-down

APP_NAME := app
MAIN := cmd/api/main.go
MIGRATE := github.com/golang-migrate/migrate/v4/cmd/migrate

build:
	go build -ldflags="-s -w" -o bin/$(APP_NAME) $(MAIN)

run:
	go run $(MAIN)

test:
	go test ./... -race -coverprofile=coverage.out

test-integration:
	go test ./... -tags integration -race

lint:
	golangci-lint run ./...

migrate-up:
	go run -tags 'postgres' $(MIGRATE) -path migrations -database "$$DATABASE_URL" up

migrate-down:
	go run -tags 'postgres' $(MIGRATE) -path migrations -database "$$DATABASE_URL" down 1

generate:
	go generate ./...
