#!/usr/bin/env bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <command> [options]"
  echo "Commands:"
  echo "  update-one    - Apply next 1 change"
  echo "  update-all    - Apply all pending changes"
  echo "  rollback-one  - Rollback last 1 change"
  echo "  rollback-tag  - Rollback to specific tag"
  echo "  status        - Show pending changes"
  echo "  history       - Show change history"
  echo "  validate      - Validate changelog"
  echo "  tag           - Tag current database state"
  exit 1
fi

COMMAND=$1
LIQUIBASE_PROPERTY=liquibase.properties

echo "COMMAND: $COMMAND | LIQUIBASE_PROPERTY: $LIQUIBASE_PROPERTY"

# Liquibase 실행
case $COMMAND in
  update-one)
    liquibase --defaults-file=$LIQUIBASE_PROPERTY update-count 1
    ;;
  update-all)
    liquibase --defaults-file=$LIQUIBASE_PROPERTY update
    ;;
  rollback-one)
    liquibase --defaults-file=$LIQUIBASE_PROPERTY rollback-count 1
    ;;
  rollback-tag)
    if [ $# -lt 2 ]; then
      echo "Usage: $0 rollback-tag <tag-name>"
      exit 1
    fi
    liquibase --defaults-file=$LIQUIBASE_PROPERTY rollback $2
    ;;
  status)
    liquibase --defaults-file=$LIQUIBASE_PROPERTY status --verbose
    ;;
  history)
    liquibase --defaults-file=$LIQUIBASE_PROPERTY history
    ;;
  validate)
    liquibase --defaults-file=$LIQUIBASE_PROPERTY validate
    ;;
  tag)
    if [ $# -lt 2 ]; then
      echo "Usage: $0 tag <tag-name>"
      exit 1
    fi
    liquibase --defaults-file=$LIQUIBASE_PROPERTY tag $2
    ;;
  *)
    echo "Unknown command: $COMMAND"
    exit 1
    ;;
esac 