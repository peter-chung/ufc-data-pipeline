# Throwaway script for testing parsing.py functions against real pasted HTML.
# Not part of the pipeline -- run directly: python -m scrapers.ufcstats._manual_test

from bs4 import BeautifulSoup

from scrapers.ufcstats.parsing import parse_stacked_cell

html = """
<div class="b-list__info-box-left clearfix">
    <div class="b-list__info-box-left">
      <i class="b-list__box-item-title">
        Career statistics:
      </i>
      <ul class="b-list__box-list b-list__box-list_margin-top">
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            SLpM:
          </i>

          4.81

        </li>
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            Str. Acc.:
          </i>
          45%
        </li>
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            SApM:
          </i>
          2.36
        </li>
        <li class="b-list__box-list-item  b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            Str. Def:
          </i>
          66%
        </li>
      </ul>
    </div>

    <div class="b-list__info-box-right b-list__info-box_style-margin-right">
      <ul class="b-list__box-list b-list__box-list_margin-top">
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_type_width">

          </i>
        </li>
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            TD Avg.:
          </i>
          0.43
        </li>
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            TD Acc.:
          </i>
          30%
        </li>
        <li class="b-list__box-list-item b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            TD Def.:
          </i>
          90%
        </li>
        <li class="b-list__box-list-item  b-list__box-list-item_type_block">
          <i class="b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width">
            Sub. Avg.:
          </i>
          0.0
        </li>
      </ul>
    </div>
  </div>
"""

soup = BeautifulSoup(html, "lxml")
td = soup.find("td")
print(parse_stacked_cell(td))
