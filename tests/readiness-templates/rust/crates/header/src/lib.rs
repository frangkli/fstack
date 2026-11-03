//! Parses one `name: value` header line.

use std::fmt;

/// A header line split into its name and value.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Header {
    name: Box<str>,
    value: Box<str>,
}

impl Header {
    /// The name before the colon, without surrounding spaces; never empty.
    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    /// The value after the colon, without surrounding spaces; may be empty.
    #[must_use]
    pub fn value(&self) -> &str {
        &self.value
    }
}

/// Why a line isn't a header.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum ParseHeaderError {
    /// The line has no colon.
    #[error("cannot find a colon in header line {line:?}")]
    MissingColon {
        /// The line as given.
        line: Box<str>,
    },
    /// Nothing but spaces comes before the colon.
    #[error("cannot read an empty header name in line {line:?}")]
    EmptyName {
        /// The line as given.
        line: Box<str>,
    },
}

impl std::str::FromStr for Header {
    type Err = ParseHeaderError;

    fn from_str(line: &str) -> Result<Self, Self::Err> {
        let Some((name, value)) = line.split_once(':') else {
            return Err(ParseHeaderError::MissingColon { line: line.into() });
        };
        let name = name.trim();
        if name.is_empty() {
            return Err(ParseHeaderError::EmptyName { line: line.into() });
        }
        Ok(Self {
            name: name.into(),
            value: value.trim().into(),
        })
    }
}

impl fmt::Display for Header {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.name, self.value)
    }
}

#[cfg(test)]
mod tests {
    use super::{Header, ParseHeaderError};
    use proptest::prelude::*;

    #[test]
    fn splits_at_the_first_colon() {
        let header: Header = "Host: example.test:8080".parse().unwrap();
        assert_eq!(
            (header.name(), header.value()),
            ("Host", "example.test:8080")
        );
    }

    #[test]
    fn rejects_a_line_without_a_colon() {
        assert_eq!(
            "Host".parse::<Header>(),
            Err(ParseHeaderError::MissingColon {
                line: "Host".into()
            })
        );
    }

    #[test]
    fn renders_a_parsed_header_normalised() {
        let header: Header = "  Accept :text/plain  ".parse().unwrap();
        insta::assert_snapshot!(header.to_string());
    }

    proptest! {
        #[test]
        fn parser_never_panics(line in any::<String>()) {
            let _ = line.parse::<Header>();
        }
    }
}
